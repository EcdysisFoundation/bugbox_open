"""
Form for the unified Data Ingestion Hub.
Handles all categories with category-specific validation.
"""

import csv
import io
from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError

from bugbox3.grower_portal.constants import (
    AVALANCHE_SAMPLE_CODE_COLUMN,
    BIRD_SITE_CODE_COLUMN,
    CATEGORY_CHOICES,
    CATEGORY_RESULT_TYPE_MAP,
    IGNITE_SAMPLE_CODE_COLUMN,
    IGNITE_SITE_TRANSECT_COLUMN,
    LABEL_PROJECT_CHOICES,
    RESULT_TYPE_CHOICES,
    RESULT_TYPE_SIGNATURE_COLUMNS,
)

_CURRENT_YEAR = date.today().year
_YEAR_CHOICES = [(y, str(y)) for y in range(2020, _CURRENT_YEAR + 2)]
_RESULT_TYPE_DISPLAY = dict(RESULT_TYPE_CHOICES)


class DataIngestionForm(forms.Form):
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label="Category",
        help_text="Select the data category you are uploading.",
    )
    result_type = forms.ChoiceField(
        choices=RESULT_TYPE_CHOICES,
        label="Data Type",
        help_text="Select the specific data type within the chosen category.",
    )
    project_type = forms.ChoiceField(
        choices=LABEL_PROJECT_CHOICES,
        label="Project Type",
        help_text="Avalanche or Ignite — must match the project type of the sample codes in the file.",
    )
    year = forms.ChoiceField(
        choices=_YEAR_CHOICES,
        label="Sampling Year",
        initial=_CURRENT_YEAR,
        help_text="Year the samples were collected.",
    )
    data_file = forms.FileField(
        label="Data File",
        help_text="CSV file (≤ 10 MB) for most categories; .xlsx for Birds.",
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Notes / Description",
        max_length=500,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.form_id = "dataIngestionForm"
        self.helper.layout = Layout(
            Row(
                Column("category",    css_class="form-group col-md-4 mb-3"),
                Column("result_type", css_class="form-group col-md-4 mb-3"),
                Column("project_type",css_class="form-group col-md-4 mb-3"),
                css_class="form-row",
            ),
            Row(
                Column("year",      css_class="form-group col-md-3 mb-3"),
                Column("data_file", css_class="form-group col-md-9 mb-3"),
                css_class="form-row",
            ),
            "description",
            Submit("submit", "Upload Data", css_class="btn btn-primary mt-2"),
        )

    # validate the data file

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("category")
        result_type = cleaned.get("result_type")

        if category and result_type:
            valid_result_types = CATEGORY_RESULT_TYPE_MAP.get(category, [])
            if result_type not in valid_result_types:
                self.add_error(
                    "result_type",
                    f"'{_RESULT_TYPE_DISPLAY.get(result_type, result_type)}' is not valid "
                    f"for the '{category}' category.",
                )
        return cleaned

    def clean_data_file(self):
        uploaded = self.cleaned_data.get("data_file")
        if not uploaded:
            return uploaded

        # Size check
        if uploaded.size > 10 * 1024 * 1024:
            raise ValidationError("File size must not exceed 10 MB.")

        category = self.data.get("category", "")
        result_type = self.data.get("result_type", "")
        project_type = self.data.get("project_type", "")

        if category == "birds":
            self._validate_bird_file(uploaded)
        else:
            self._validate_generic_csv(uploaded, project_type, result_type)

        return uploaded

    # validate the generic csv file

    def _validate_generic_csv(self, uploaded, project_type, result_type):
        if not uploaded.name.endswith(".csv"):
            raise ValidationError("File must have a .csv extension.")

        try:
            uploaded.seek(0)
            content = uploaded.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            headers = reader.fieldnames or []
        except (csv.Error, UnicodeDecodeError) as exc:
            raise ValidationError(f"Could not read CSV file: {exc}") from exc

        if not headers:
            raise ValidationError("CSV file appears to be empty or has no headers.")
        if any(not h for h in headers):
            raise ValidationError("CSV file contains empty header values.")

        cleaned_headers = [h.strip() for h in headers]

        # Sample-code column presence
        if project_type == "avalanche":
            if AVALANCHE_SAMPLE_CODE_COLUMN not in cleaned_headers:
                raise ValidationError(
                    f"Missing required column '{AVALANCHE_SAMPLE_CODE_COLUMN}' "
                    f"for Avalanche project type."
                )
        elif project_type == "ignite":
            for required in (IGNITE_SAMPLE_CODE_COLUMN, IGNITE_SITE_TRANSECT_COLUMN):
                if required not in cleaned_headers:
                    raise ValidationError(
                        f"Missing required column '{required}' for Ignite project type."
                    )

        # Depth columns for Basic
        if result_type == "basic":
            for col in ("Beginning Depth", "Ending Depth"):
                if col not in cleaned_headers:
                    raise ValidationError(f"'{col}' header is required for Basic result type.")

        # Signature column check
        sig_cols = RESULT_TYPE_SIGNATURE_COLUMNS.get(result_type, [])
        if sig_cols and not any(c in cleaned_headers for c in sig_cols):
            display = _RESULT_TYPE_DISPLAY.get(result_type, result_type)
            raise ValidationError(
                f"This file does not appear to be a {display} file. "
                f"Expected at least one of: {', '.join(sig_cols[:3])}…"
            )

    def _validate_bird_file(self, uploaded):
        name_lower = uploaded.name.lower()
        if not (name_lower.endswith(".xlsx") or name_lower.endswith(".xls") or name_lower.endswith(".csv")):
            raise ValidationError("Bird data file must be an Excel (.xlsx/.xls) or CSV file.")

        if name_lower.endswith(".csv"):
            # CSV birds: validate headers
            try:
                uploaded.seek(0)
                content = uploaded.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8-sig")
                reader = csv.DictReader(io.StringIO(content))
                headers = [h.strip() for h in (reader.fieldnames or [])]
            except Exception as exc:
                raise ValidationError(f"Could not read bird CSV: {exc}") from exc

            sig_cols = RESULT_TYPE_SIGNATURE_COLUMNS.get("birds", [])
            if not any(c in headers for c in sig_cols):
                raise ValidationError(
                    f"Bird CSV must contain at least one of: {', '.join(sig_cols)}."
                )
            return

        # xlsx: check row 2 (data header) contains required bird columns
        try:
            import openpyxl

            uploaded.seek(0)
            wb = openpyxl.load_workbook(uploaded, read_only=True, data_only=True)
            ws = wb.worksheets[0]
            rows = list(ws.iter_rows(max_row=3, values_only=True))
            wb.close()
        except Exception as exc:
            raise ValidationError(f"Could not read Excel file: {exc}") from exc

        if len(rows) < 2:
            raise ValidationError("Bird Excel file must have at least 2 header rows plus data.")

        data_header = [str(c).strip() if c is not None else "" for c in rows[1]]

        if BIRD_SITE_CODE_COLUMN not in data_header:
            raise ValidationError(
                f"Bird file must contain column '{BIRD_SITE_CODE_COLUMN}' in row 2."
            )

        sig_cols = RESULT_TYPE_SIGNATURE_COLUMNS.get("birds", [])
        if not any(c in data_header for c in sig_cols):
            raise ValidationError(
                f"Bird file (row 2) must contain at least one of: {', '.join(sig_cols)}."
            )
