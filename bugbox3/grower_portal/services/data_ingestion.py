"""
Centralised ingestion service for all Grower Portal data categories.

Entry points
------------
build_s3_path(category, result_type, year, filename)
    Returns the organised S3 key for any uploaded file.

process_generic_csv(csv_import_log, csv_file, project_type, result_type)
    Handles soils / water / plants — standard single-header CSV.

process_bird_csv(csv_import_log, xlsx_file)
    Handles the Bird point-count spreadsheet
    ``CSVImportLog.project_type`` is set from each row’s ``SampleCode.project_type``
    (the upload form still captures intent; if it disagrees, a warning is recorded).

Validation behaviour
--------------------
- Valid rows are always committed even when some rows fail (partial success).
- Row-level errors are collected and stored on CSVImportLog.error_log.
- Status is set to:
    "completed"              — all rows OK
    "completed_with_errors"  — some rows OK, some failed
    "failed"                 — zero rows imported
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any

import openpyxl
from django.db import transaction

from bugbox3.grower_portal.constants import (
    AVALANCHE_SAMPLE_CODE_COLUMN,
    BIRD_DATA_HEADER_ROW,
    BIRD_FAMILY_HEADER_ROW,
    BIRD_SITE_CODE_COLUMN,
    GROWER_DATA_S3_PREFIX,
    IGNITE_SAMPLE_CODE_COLUMN,
    IGNITE_SITE_TRANSECT_COLUMN,
)
from bugbox3.grower_portal.models.csv_import import CSVImportFieldValue, CSVImportRow
from bugbox3.grower_portal.models.sample_codes import SampleCode, SiteTransect

# Columns in bird files where the value must be numeric (or empty)
_BIRD_NUMERIC_COLUMNS = {'Abundance', 'Richness', 'Duration (min)', 'Distance KM'}
# Stored field values are skipped for these columns (ignored at ingest).
_BIRD_COLUMNS_SKIP_STORE = frozenset({'Matrix Score'})
# Excel cell error strings returned by openpyxl
_EXCEL_ERROR_VALUES = {'#DIV/0!', '#N/A', '#NAME?', '#NULL!', '#NUM!', '#REF!', '#VALUE!', '#ERROR!'}


# helpers

def build_s3_path(category: str, result_type: str, year: int | str, filename: str) -> str:
    """Return ``grower_portal_data/{category}/{result_type}/{year}/{filename}``."""
    return f"{GROWER_DATA_S3_PREFIX}/{category}/{result_type}/{year}/{filename}"


def _add_error(error_log: list, row_number: int, row: Any, message: str) -> None:
    error_log.append({"row_number": row_number, "row_data": row, "error": message})


def _add_warning(error_log: list, row_number: int, row: Any, message: str) -> None:
    """row still saved, but admin is informed."""
    error_log.append({"row_number": row_number, "row_data": row, "warning": message})


def _normalise_cell_value(value: Any) -> str:
    """
    Convert an openpyxl cell value to a clean string:
    - datetime / date -> date string "YYYY-MM-DD"
    - excel error strings -> empty string
    - none -> ""
    - everything else -> str
    """
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if hasattr(value, "date"):  # date (not datetime)
        return str(value)
    str_val = str(value)
    if str_val in _EXCEL_ERROR_VALUES:
        return ""
    return str_val.strip()


def _is_excel_error(value: Any) -> bool:
    return str(value) in _EXCEL_ERROR_VALUES if value is not None else False


def _validate_numeric(value: Any) -> bool:
    """Return True if value is numeric, empty, or a valid numeric range; False if unexpected text"""
    if value is None or value == "":
        return True
    s = str(value).strip()
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        pass
    # Accept numeric ranges example:: "88-91", "10.5-12.0"
    return _is_numeric_range(s)


def _is_numeric_range(s: str) -> bool:
    """
    Return True if s looks like a numeric range, e.g. "88-91" or "10.5-12.0".
    must have exactly two numeric parts separated by -
    """
    parts = s.split("-")
    if len(parts) != 2:
        return False
    try:
        float(parts[0].strip())
        float(parts[1].strip())
        return True
    except (ValueError, TypeError):
        return False


def _range_midpoint(s: str) -> float | None:
    """Return the midpoint of a range string, or None if not parseable."""
    parts = s.split("-")
    if len(parts) != 2:
        return None
    try:
        lo = float(parts[0].strip())
        hi = float(parts[1].strip())
        return (lo + hi) / 2
    except (ValueError, TypeError):
        return None


# Generic CSV ingestion With soils / water / plants

def _validate_sample_code(row_number, row, error_log, project_type):
    col = AVALANCHE_SAMPLE_CODE_COLUMN if project_type == "avalanche" else IGNITE_SAMPLE_CODE_COLUMN
    code = (row.get(col) or "").strip()
    if not code:
        _add_error(error_log, row_number, row, f"Missing sample code in column '{col}'.")
        return None
    try:
        return SampleCode.objects.get(code=code, project_type=project_type)
    except SampleCode.DoesNotExist:
        _add_error(
            error_log, row_number, row,
            f"Sample code '{code}' not found in the database for project type '{project_type}'.",
        )
        return None


def _validate_site_transect(row_number, row, error_log, sample_code_obj):
    transect_raw = (row.get(IGNITE_SITE_TRANSECT_COLUMN) or "").strip()
    if not transect_raw:
        _add_error(
            error_log, row_number, row,
            f"Missing transect number in column '{IGNITE_SITE_TRANSECT_COLUMN}'.",
        )
        return None
    try:
        return SiteTransect.objects.get(
            site_code=sample_code_obj,
            transect_number=transect_raw,
        )
    except SiteTransect.DoesNotExist:
        _add_error(
            error_log, row_number, row,
            f"Transect '{transect_raw}' not found for site '{sample_code_obj.code}'.",
        )
        return None


def _delete_existing_rows_for_codes(sample_codes: list, result_type: str, project_type: str) -> int:
    """
    Delete all CSVImportRows (and cascaded FieldValues) for the given sample codes,
    result type and project type.  (re-uploads fully replaces prior data)

    returns the number of rows deleted
    """
    if project_type == "ignite":
        qs = CSVImportRow.objects.filter(
            site_transect__site_code__in=sample_codes,
            import_log__result_type=result_type,
            import_log__project_type=project_type,
        )
    else:
        qs = CSVImportRow.objects.filter(
            sample_code__in=sample_codes,
            import_log__result_type=result_type,
            import_log__project_type=project_type,
        )
    count, _ = qs.delete()
    return count


def process_generic_csv(csv_import_log, csv_file, project_type: str, result_type: str):
    """
    Parse a standard single-header CSV and persist rows + field values.

    Re-upload behaviour (soils / water / plants):
    Any existing rows for the sample codes present in this file are deleted
    before the new rows are saved

    Returns ``(total, successful, failed, error_log)``.
    """
    csv_file.seek(0)
    content = csv_file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(content))
    successful = 0
    failed = 0
    error_log: list = []
    import_rows: list[CSVImportRow] = []
    import_field_values: list[CSVImportFieldValue] = []

    for i, row in enumerate(reader):
        try:
            sample_code_obj = _validate_sample_code(i, row, error_log, project_type)
            if not sample_code_obj:
                failed += 1
                continue

            site_transect_obj = None
            if project_type == "ignite":
                site_transect_obj = _validate_site_transect(i, row, error_log, sample_code_obj)
                if not site_transect_obj:
                    failed += 1
                    continue

            cleaned = {k.strip(): v for k, v in row.items()}
            beginning = cleaned.get("Beginning Depth ", "") or cleaned.get("Beginning Depth", "")
            ending = cleaned.get("Ending Depth", "")
            depth = f"{beginning}-{ending}" if (beginning or ending) else None

            import_row = CSVImportRow(
                import_log=csv_import_log,
                sample_code=sample_code_obj,
                site_transect=site_transect_obj,
                depth=depth,
                row_number=i,
            )
            import_rows.append(import_row)

            for field_name, field_value in cleaned.items():
                import_field_values.append(
                    CSVImportFieldValue(
                        field_name=field_name,
                        field_value=field_value or "",
                        row=import_row,
                    )
                )
            successful += 1

        except Exception as exc:
            failed += 1
            _add_error(error_log, i, row, f"Unexpected error: {exc}")

    # Replace previous data for any sample codes present in this file,
    # then save the new rows. all in one atomic transaction.
    if import_rows:
        saved_codes = list({r.sample_code for r in import_rows if r.sample_code_id})
        saved_transects = list({r.site_transect for r in import_rows if r.site_transect_id})
        replace_codes = saved_transects if project_type == "ignite" else saved_codes

        with transaction.atomic():
            deleted = _delete_existing_rows_for_codes(replace_codes, result_type, project_type)
            if deleted:
                _add_warning(
                    error_log, 0, {},
                    f"{deleted} previously imported row(s) for the site code(s) in this file "
                    f"were replaced by the new data.",
                )
            CSVImportRow.objects.bulk_create(import_rows)
            CSVImportFieldValue.objects.bulk_create(import_field_values)

    total = successful + failed
    return total, successful, failed, error_log


# Bird-specific ingestion

def _normalize_site_code(raw) -> str:
    """Convert 1000.0 / '1000.0' / 1000 all to '1000'."""
    if raw is None:
        return ""
    try:
        return str(int(float(str(raw).strip())))
    except (ValueError, TypeError):
        return str(raw).strip()


def _split_site_codes(raw) -> list[str]:
    """
    Return one or more normalised site code strings from a cell value.

    handles "4273/4274" -> ["4273", "4274"].
    single codes example: 4001.0 -> ["4001"]
    returns [] if the value is blank/unparseable
    """
    if raw is None:
        return []
    raw_str = str(raw).strip()
    if not raw_str:
        return []
    parts = [p.strip() for p in raw_str.split("/") if p.strip()]
    result = []
    for p in parts:
        try:
            result.append(str(int(float(p))))
        except (ValueError, TypeError):
            result.append(p)
    return result


def _build_family_map(header_row: tuple, data_header_row: tuple) -> dict[str, str]:
    """
    Build {species_column_name: family_name} from the two header rows.

    ``header_row``      — row 0 from the xlsx (family names, with None gaps).
    ``data_header_row`` — row 1 from the xlsx (actual column names)
    """
    family_map: dict[str, str] = {}
    current_family = ""
    for family_val, col_name in zip(header_row, data_header_row):
        if family_val is not None:
            current_family = str(family_val).strip()
        if col_name is not None:
            col_str = str(col_name).strip()
            if col_str and current_family:
                family_map[col_str] = current_family
    return family_map


def _check_duplicate_survey(sample_code_obj, date_str: str, project_type: str) -> bool:
    """
    Return True if a bird survey row for this site+date already exists in the DB
    """
    if not date_str:
        return False
    return CSVImportFieldValue.objects.filter(
        field_name="Date",
        field_value=date_str,
        row__sample_code=sample_code_obj,
        row__import_log__result_type="birds",
        row__import_log__project_type=project_type,
    ).exists()


def process_bird_csv(csv_import_log, xlsx_file):
    """
    Parse a Bird point-count Excel file
      row 0 : family-header row
      row 1 : real column headers
      row 2+ : data rows (one row = one survey event)

    Validation performed per row:
    - Site Code must not be blank and must exist in the SampleCode table.
    - Numeric columns (Abundance, Richness, species counts) must be numeric or empty.
    - Excel error values (#DIV/0! etc.) are cleared and flagged as warnings.
    - Duplicate Site Code + Date combinations within the DB are flagged as warnings

    Valid rows are committed. rows with hard errors (missing/bad site code)
    are skipped and counted as failed.

    Returns ``(total, successful, failed, error_log)``.
    """
    xlsx_file.seek(0)
    wb = openpyxl.load_workbook(xlsx_file, read_only=True, data_only=True)
    sheet = wb.worksheets[0]
    rows = list(sheet.iter_rows(values_only=True))
    wb.close()

    if len(rows) < 3:
        return 0, 0, 0, [{"row_number": 0, "row_data": {}, "error": "File has fewer than 3 rows."}]

    family_header_row = rows[BIRD_FAMILY_HEADER_ROW]
    data_header_row = rows[BIRD_DATA_HEADER_ROW]
    data_rows = rows[BIRD_DATA_HEADER_ROW + 1:]

    # Store species→family mapping for grower-facing tables (does not overwrite admin notes)
    family_map = _build_family_map(family_header_row, data_header_row)
    meta = dict(csv_import_log.ingestion_metadata or {})
    meta["family_map"] = family_map
    csv_import_log.ingestion_metadata = meta
    csv_import_log.save(update_fields=["ingestion_metadata"])

    col_names = [str(c).strip() if c is not None else "" for c in data_header_row]

    successful = 0
    failed = 0
    error_log: list = []
    import_rows: list[CSVImportRow] = []
    import_field_values_map: dict[int, list[CSVImportFieldValue]] = {}
    # Birds: project type (Avalanche vs Ignite) comes from SampleCode, not the upload form.
    file_project_type: str | None = None
    declared_project_type = csv_import_log.project_type

    for i, raw_row in enumerate(data_rows):
        excel_row_number = i + BIRD_DATA_HEADER_ROW + 2

        # Skip completely empty rows
        if all(v is None for v in raw_row):
            continue

        row_dict_raw = {
            col_names[j]: raw_row[j]
            for j in range(min(len(col_names), len(raw_row)))
        }

        try:
            # Site Code: error if missing or not in DB
            raw_code = row_dict_raw.get(BIRD_SITE_CODE_COLUMN)
            site_code_strs = _split_site_codes(raw_code)

            if not site_code_strs:
                _add_error(
                    error_log, excel_row_number, {},
                    f"Row {excel_row_number}: Missing or blank Site Code.",
                )
                failed += 1
                continue

            # resolve each code to a SampleCode object
            sample_code_objs: list[SampleCode] = []
            all_codes_valid = True
            for site_code_str in site_code_strs:
                try:
                    sample_code_objs.append(SampleCode.objects.get(code=site_code_str))
                except SampleCode.DoesNotExist:
                    _add_error(
                        error_log, excel_row_number, {"Site Code": site_code_str},
                        f"Row {excel_row_number}: Site Code '{site_code_str}' not found in "
                        f"the database. Ensure it has been created before uploading bird data.",
                    )
                    all_codes_valid = False

            if not all_codes_valid:
                failed += 1
                continue

            project_types_for_row = {obj.project_type for obj in sample_code_objs}
            if len(project_types_for_row) > 1:
                _add_error(
                    error_log, excel_row_number, {"Site Code": raw_code},
                    f"Row {excel_row_number}: Site Codes in this row belong to different programs "
                    f"({project_types_for_row}). Use one program per sheet row.",
                )
                failed += 1
                continue

            row_program = next(iter(project_types_for_row))
            if file_project_type is None:
                file_project_type = row_program
            elif row_program != file_project_type:
                lc = {"avalanche": "Avalanche", "ignite": "Ignite"}
                _add_error(
                    error_log, excel_row_number, {"Site Code": raw_code},
                    f"Row {excel_row_number}: This row’s site code is {lc.get(row_program, row_program)} "
                    f"but earlier rows in the file are {lc.get(file_project_type, file_project_type)}. "
                    f"Put Avalanche and Ignite bird data in separate uploads.",
                )
                failed += 1
                continue

            if len(site_code_strs) > 1:
                _add_warning(
                    error_log, excel_row_number,
                    {"Site Code": raw_code},
                    f"Row {excel_row_number}: Shared survey across sites "
                    f"{', '.join(site_code_strs)}. Survey data will be saved for each site.",
                )

            # Normalise all cell values
            row_dict_clean: dict[str, str] = {}
            for col, value in row_dict_raw.items():
                if not col:
                    continue
                if _is_excel_error(value):
                    _add_warning(
                        error_log, excel_row_number, {"column": col},
                        f"Row {excel_row_number}, column '{col}': Excel error value "
                        f"({value}) replaced with empty.",
                    )
                    row_dict_clean[col] = ""
                else:
                    row_dict_clean[col] = _normalise_cell_value(value)

            # Numeric validation for key columns
            for numeric_col in _BIRD_NUMERIC_COLUMNS:
                val = row_dict_clean.get(numeric_col, "")
                if val and not _validate_numeric(val):
                    _add_warning(
                        error_log, excel_row_number, {"column": numeric_col, "value": val},
                        f"Row {excel_row_number}, column '{numeric_col}': expected a number "
                        f"but got '{val}'. Value stored as-is; check your source data.",
                    )

            date_str = row_dict_clean.get("Date", "")

            # Build one CSVImportRow per site code
            for sample_code_obj in sample_code_objs:
                # Duplicate survey warning (per site)
                if _check_duplicate_survey(sample_code_obj, date_str, row_program):
                    _add_warning(
                        error_log, excel_row_number,
                        {"Site Code": sample_code_obj.code, "Date": date_str},
                        f"Row {excel_row_number}: A bird survey for site "
                        f"'{sample_code_obj.code}' on '{date_str}' is already in the "
                        f"database. Row still saved (bird data is additive). Delete the "
                        f"previous import from Import History if this was a re-upload.",
                    )

                import_row = CSVImportRow(
                    import_log=csv_import_log,
                    sample_code=sample_code_obj,
                    site_transect=None,
                    depth=None,
                    row_number=excel_row_number,
                )
                import_rows.append(import_row)
                import_field_values_map[f"{i}_{sample_code_obj.code}"] = [
                    CSVImportFieldValue(
                        field_name=col,
                        field_value=val,
                        row=import_row,
                    )
                    for col, val in row_dict_clean.items()
                    if col and col not in _BIRD_COLUMNS_SKIP_STORE
                ]

            successful += 1

        except Exception as exc:
            failed += 1
            _add_error(
                error_log, excel_row_number, {},
                f"Row {excel_row_number}: Unexpected error — {exc}",
            )

    # Set project_type on the import log from SampleCode
    if successful > 0 and file_project_type:
        lc = {"avalanche": "Avalanche", "ignite": "Ignite"}
        declared_label = lc.get(declared_project_type, declared_project_type)
        inferred_label = lc.get(file_project_type, file_project_type)
        if file_project_type != declared_project_type:
            _add_warning(
                error_log, 0, {},
                f"The upload form showed Project type “{declared_label}”, but Site Codes in "
                f"this file are “{inferred_label}” sites. The import is stored as "
                f"“{inferred_label}”. Growers pick that program on My Results to view birds.",
            )
        csv_import_log.project_type = file_project_type
        csv_import_log.save(update_fields=["project_type"])

    # Always commit valid rows
    if import_rows:
        with transaction.atomic():
            CSVImportRow.objects.bulk_create(import_rows)
            all_fvs = [fv for fvs in import_field_values_map.values() for fv in fvs]
            CSVImportFieldValue.objects.bulk_create(all_fvs)

    total = successful + failed
    return total, successful, failed, error_log
