from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import re
from copy import deepcopy

from ..models import TransectCode
from bugbox3.core.models import PublicSiteContent
from ..constants import (
    SAMPLE_TYPES,
    LABEL_TEMPLATE_SLUG
)


class LabelGenerator:
    """Service for generating label documents"""
    
    def __init__(self, project_type, cluster_number, year, sample_types, labels_per_type, created_by):
        self.project_type = project_type
        self.cluster_number = cluster_number
        self.year = year
        self.sample_types = sample_types
        self.labels_per_type = labels_per_type
        self.created_by = created_by
        self.generated_codes = []
    
    def get_sample_type_display(self, sample_type_code):
        choices = dict(SAMPLE_TYPES)
        return choices.get(sample_type_code, sample_type_code)
    
    def generate_unique_transect_codes(self, count):
        """Generate unique numeric transect codes"""
        codes = []
        
        all_codes = TransectCode.objects.all().values_list('transect_code', flat=True)
        
        max_code = 0
        for code in all_codes:
            try:
                num = int(code)
                max_code = max(max_code, num)
            except ValueError:
                digits = re.findall(r'\d+', code)
                if digits:
                    num = int(digits[-1])
                    max_code = max(max_code, num)
        
        for i in range(count):
            new_code = str(max_code + i + 1).zfill(6)
            codes.append(new_code)
        
        return codes
    
    def save_transect_codes(self, codes):
        """Save generated transect codes to database"""
        transect_code_objects = [
            TransectCode(
                transect_code=code,
                is_active=True,
                is_used=False,
                created_by=self.created_by
            )
            for code in codes
        ]
        TransectCode.objects.bulk_create(transect_code_objects)
        self.generated_codes = codes
    
    def create_label_text(self, sample_type_display, transect_code):
        """Create label text based on project type"""
        if self.project_type == 'avalanche':
            # Avalanche format: Sample Type / Cluster-Year / Transect Code
            return f"{sample_type_display}\n{self.cluster_number} – {self.year}\n{transect_code}"
        else:
            # 1000 Farms format: Cluster-Year / Sample Type / Transect Code
            return f"{self.cluster_number} – {self.year}\n{sample_type_display}\n{transect_code}"
    
    def _load_template(self):
        """Load the template document from PublicSiteContent"""
        try:
            template_content = PublicSiteContent.objects.get(title=LABEL_TEMPLATE_SLUG)
            
            if not template_content.file:
                raise ValueError(
                    f"Label template '{LABEL_TEMPLATE_SLUG}' found in PublicSiteContent but file is missing. Please upload it in Django Admin"
                )
            
            with template_content.file.open('rb') as file:
                file_content = file.read()
                file_buffer = BytesIO(file_content)
                try:
                    return Document(file_buffer)
                except Exception as e:
                    error_msg = str(e)
                    if 'not a Word file' in error_msg or 'content type' in error_msg.lower():
                        raise ValueError(
                            f"Template file '{LABEL_TEMPLATE_SLUG}' could not be loaded. Please save your template as '.docx' "
                            f"Original error: {error_msg}"
                        ) from e
                    else:
                        raise
        
        except PublicSiteContent.DoesNotExist:
            raise ValueError(
                f"Label template '{LABEL_TEMPLATE_SLUG}' not found in PublicSiteContent. "
            )
        except Exception as e:
            raise ValueError(
                f"Error loading label template: {str(e)}"
            ) from e
    
    def _replace_cell_text_preserving_format(self, cell, new_text):
        """Replace cell text by modifying existing runs"""
        if not cell.paragraphs:
            cell.add_paragraph()
        
        paragraph = cell.paragraphs[0]
        
        if paragraph.runs:
            runs = list(paragraph.runs)
            
            first_run = runs[0]
            first_run.text = new_text
            
            for r in runs[1:]:
                r._element.getparent().remove(r._element)
        else:
            if paragraph.text.strip():
                paragraph.clear()
            
            run = paragraph.add_run(new_text)
            run.font.size = Pt(11)
            run.font.bold = True
        
        return paragraph
    
    def _remove_pages_after_last_filled_cell(self, doc):
        """Find the last filled cell (with sample type and/or transect code) and remove all pages after it"""
        if not doc.tables:
            return
        
        last_filled_table_idx = -1
        last_filled_cell_info = None
        
        for table_idx in range(len(doc.tables) - 1, -1, -1):
            try:
                table = doc.tables[table_idx]
                for row_idx, row in enumerate(table.rows):
                    try:
                        if not hasattr(row, 'cells'):
                            continue
                        for col_idx, cell in enumerate(row.cells):
                            try:
                                cell_text = cell.text.strip()
                                if cell_text and cell_text.upper() != 'LABEL' and len(cell_text) > 1:
                                    has_sample_type = any(char.isalpha() for char in cell_text)
                                    has_transect_code = any(char.isdigit() for char in cell_text)
                                    has_multiline = '\n' in cell_text
                                    
                                    if (has_sample_type or has_transect_code) and (has_transect_code or has_multiline):
                                        if last_filled_table_idx < 0 or table_idx > last_filled_table_idx:
                                            last_filled_table_idx = table_idx
                                            last_filled_cell_info = {
                                                'table_idx': table_idx,
                                                'row_idx': row_idx,
                                                'col_idx': col_idx
                                            }
                            except (AttributeError, IndexError):
                                continue
                    except (IndexError, AttributeError):
                        continue
            except (IndexError, AttributeError):
                continue
        
        if last_filled_table_idx >= 0 and last_filled_table_idx < len(doc.tables) - 1:
            tables_to_remove = list(range(len(doc.tables) - 1, last_filled_table_idx, -1))
            
            for idx in tables_to_remove:
                try:
                    if idx < len(doc.tables):
                        table_element = doc.tables[idx]._tbl
                        parent = table_element.getparent()
                        if parent is not None:
                            parent.remove(table_element)
                except (IndexError, AttributeError, ValueError):
                    pass
        
        try:
            if doc.tables:
                last_table_idx = len(doc.tables) - 1
                if last_table_idx >= 0:
                    last_table_element = doc.tables[last_table_idx]._tbl
                    parent = last_table_element.getparent()
                    if parent is not None:
                        try:
                            last_table_index = list(parent).index(last_table_element)
                        except ValueError:
                            last_table_index = -1
                        
                        if last_table_index >= 0:
                            all_elements = list(parent)
                            elements_after_table = all_elements[last_table_index + 1:]
                            
                            for elem in reversed(elements_after_table):
                                try:
                                    if elem.tag.endswith('}p'):
                                        para_text = ''.join(elem.itertext()).strip()
                                        if not para_text:
                                            try:
                                                parent.remove(elem)
                                            except (ValueError, AttributeError):
                                                pass
                                except (ValueError, AttributeError):
                                    pass
        except (IndexError, AttributeError, ValueError):
            pass
    
    def _template_has_placeholders(self, doc):
        """Check if template has LABEL placeholders"""
        if not doc.tables:
            return False
        
        for table in doc.tables:
            try:
                for row in table.rows:
                    try:
                        if not hasattr(row, 'cells'):
                            continue
                        for cell in row.cells:
                            try:
                                if 'LABEL' in cell.text.upper():
                                    return True
                            except (AttributeError, IndexError):
                                continue
                    except (IndexError, AttributeError):
                        continue
            except (IndexError, AttributeError):
                continue
        return False
    
    def _fill_template_with_placeholders(self, doc, labels_by_column):
        """Fill template using placeholder replacement"""
        if not doc.tables:
            return doc
        
        if not labels_by_column:
            return doc
        
        num_sample_types = len(labels_by_column)
        label_index_by_sample_type = [0] * num_sample_types
        
        if not doc.tables or len(doc.tables) == 0:
            return doc
        
        first_table = None
        for table in doc.tables:
            try:
                if len(table.rows) > 0:
                    first_row = table.rows[0]
                    if hasattr(first_row, 'cells') and len(first_row.cells) > 0:
                        _ = first_row.cells[0]
                        first_table = table
                        break
            except (IndexError, AttributeError):
                continue
        
        if first_table is None:
            return doc
        
        original_template_table_xml = deepcopy(first_table._tbl)
        original_table_style = first_table.style if first_table.style else None
        
        original_style_val = None
        try:
            original_tbl_pr = first_table._tbl.tblPr
            if original_tbl_pr is not None:
                for child in original_tbl_pr:
                    if 'tblStyle' in child.tag:
                        original_style_val = child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                        break
        except Exception:
            pass
        
        template_cols_with_label = []
        if first_table.rows:
            try:
                first_row = first_table.rows[0]
                num_cells = len(first_row.cells) if hasattr(first_row, 'cells') else 0
                for col_idx in range(num_cells):
                    try:
                        cell = first_row.cells[col_idx]
                        if 'LABEL' in cell.text.upper():
                            template_cols_with_label.append(col_idx)
                    except (IndexError, AttributeError):
                        continue
            except (IndexError, AttributeError):
                for row in first_table.rows:
                    try:
                        if len(row.cells) > 0:
                            for col_idx in range(len(row.cells)):
                                try:
                                    cell = row.cells[col_idx]
                                    if 'LABEL' in cell.text.upper() and col_idx not in template_cols_with_label:
                                        template_cols_with_label.append(col_idx)
                                except (IndexError, AttributeError):
                                    continue
                            if template_cols_with_label:
                                break
                    except (IndexError, AttributeError):
                        continue
        
        if not template_cols_with_label:
            return doc
        
        num_cols_available = len(template_cols_with_label)
        
        total_labels_needed = sum(len(col_labels) for col_labels in labels_by_column)
        
        labels_per_table = 0
        for row in first_table.rows:
            try:
                num_cells = len(row.cells) if hasattr(row, 'cells') else 0
                for col_idx in template_cols_with_label:
                    if col_idx < num_cells:
                        try:
                            cell = row.cells[col_idx]
                            if 'LABEL' in cell.text.upper():
                                labels_per_table += 1
                        except (IndexError, AttributeError):
                            continue
            except (IndexError, AttributeError):
                continue
        
        labels_per_sample_type_per_table = labels_per_table // num_cols_available if num_cols_available > 0 else labels_per_table
        
        max_labels_per_sample_type = max(len(col_labels) for col_labels in labels_by_column) if labels_by_column else 0
        tables_per_sample_type = max(1, (max_labels_per_sample_type + labels_per_sample_type_per_table - 1) // labels_per_sample_type_per_table) if labels_per_sample_type_per_table > 0 else 1
        
        tables_needed = max(1, (tables_per_sample_type * num_sample_types + num_cols_available - 1) // num_cols_available) if num_cols_available > 0 else tables_per_sample_type * num_sample_types
        
        tables_needed = min(tables_needed, 100)
        
        existing_tables = len(doc.tables)
        tables_to_create = max(0, tables_needed - existing_tables)
        
        if tables_to_create > 0:
            batch_size = 10
            for batch_start in range(0, tables_to_create, batch_size):
                batch_end = min(batch_start + batch_size, tables_to_create)
                for i in range(batch_start, batch_end):
                    doc.add_page_break()
                    
                    new_tbl = deepcopy(original_template_table_xml)
                    doc._body._body.append(new_tbl)
                    
                    new_table = doc.tables[-1]
                    
                    if original_style_val:
                        try:
                            new_tbl_pr = new_table._tbl.get_or_add_tblPr()
                            
                            has_style_in_xml = False
                            for child in new_tbl_pr:
                                if 'tblStyle' in child.tag:
                                    has_style_in_xml = True
                                    existing_val = child.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                                    if existing_val != original_style_val:
                                        child.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', original_style_val)
                                    break
                            
                            if not has_style_in_xml:
                                from docx.oxml import OxmlElement
                                from docx.oxml.ns import qn
                                tbl_style = OxmlElement('w:tblStyle')
                                tbl_style.set(qn('w:val'), original_style_val)
                                new_tbl_pr.append(tbl_style)
                            
                            if original_table_style:
                                new_table.style = original_table_style
                        except Exception:
                            try:
                                if original_table_style:
                                    new_table.style = original_table_style
                            except Exception:
                                pass
        
        current_sample_type_batch = 0
        
        filled_table_indices = []
        
        labels_per_sample_type_per_table = labels_per_table // num_cols_available if num_cols_available > 0 else labels_per_table
        
        for table_idx, table in enumerate(doc.tables):
            try:
                if len(table.rows) < 1:
                    continue
                if not hasattr(table.rows[0], 'cells') or len(table.rows[0].cells) == 0:
                    continue
            except (IndexError, AttributeError):
                continue
            
            col_to_sample_type = {}
            for i, template_col_idx in enumerate(template_cols_with_label):
                sample_type_idx = current_sample_type_batch * num_cols_available + i
                if sample_type_idx < num_sample_types:
                    if label_index_by_sample_type[sample_type_idx] < len(labels_by_column[sample_type_idx]):
                        col_to_sample_type[template_col_idx] = sample_type_idx
            
            if not col_to_sample_type:
                current_sample_type_batch += 1
                col_to_sample_type = {}
                for i, template_col_idx in enumerate(template_cols_with_label):
                    sample_type_idx = current_sample_type_batch * num_cols_available + i
                    if sample_type_idx < num_sample_types:
                        if label_index_by_sample_type[sample_type_idx] < len(labels_by_column[sample_type_idx]):
                            col_to_sample_type[template_col_idx] = sample_type_idx
                
                if not col_to_sample_type:
                    break
            
            table_was_filled = False
            
            for row in table.rows:
                try:
                    num_cells = len(row.cells) if hasattr(row, 'cells') else 0
                except (IndexError, AttributeError):
                    continue
                
                for template_col_idx in col_to_sample_type.keys():
                    if template_col_idx >= num_cells:
                        continue
                    
                    try:
                        cell = row.cells[template_col_idx]
                        cell_text = cell.text.strip().upper()
                    except (IndexError, AttributeError):
                        continue
                    
                    if 'LABEL' in cell_text:
                        sample_type_idx = col_to_sample_type[template_col_idx]
                        
                        if label_index_by_sample_type[sample_type_idx] < len(labels_by_column[sample_type_idx]):
                            label_text = labels_by_column[sample_type_idx][label_index_by_sample_type[sample_type_idx]]
                            label_index_by_sample_type[sample_type_idx] += 1
                            table_was_filled = True
                            
                            replaced = False
                            
                            if cell.paragraphs:
                                for paragraph in cell.paragraphs:
                                    if paragraph.runs:
                                        for run in paragraph.runs:
                                            run_text_upper = run.text.upper()
                                            if 'LABEL' in run_text_upper:
                                                fmt_size = run.font.size
                                                fmt_bold = run.font.bold
                                                fmt_name = run.font.name
                                                
                                                new_run_text = re.sub(r'LABEL', label_text, run.text, flags=re.IGNORECASE)
                                                run.text = new_run_text
                                                
                                                if fmt_size:
                                                    run.font.size = fmt_size
                                                if fmt_bold is not None:
                                                    run.font.bold = fmt_bold
                                                if fmt_name:
                                                    run.font.name = fmt_name
                                                
                                                replaced = True
                                                break
                                    if replaced:
                                        break
                            
                            if not replaced:
                                new_text = re.sub(r'LABEL', label_text, cell.text, flags=re.IGNORECASE)
                                cell.text = new_text
                                
                                if cell.paragraphs:
                                    for paragraph in cell.paragraphs:
                                        for run in paragraph.runs:
                                            if not run.font.size:
                                                run.font.size = Pt(11)
                                            if run.font.bold is None:
                                                run.font.bold = True
                
                if all(label_index_by_sample_type[sample_type_idx] >= len(labels_by_column[sample_type_idx]) 
                       for sample_type_idx in range(num_sample_types)):
                    break
            
            if table_was_filled:
                filled_table_indices.append(table_idx)
            
            all_current_batch_filled = True
            for sample_type_idx in col_to_sample_type.values():
                if label_index_by_sample_type[sample_type_idx] < len(labels_by_column[sample_type_idx]):
                    all_current_batch_filled = False
                    break
            
            if all_current_batch_filled:
                current_sample_type_batch += 1
            
            if all(label_index_by_sample_type[sample_type_idx] >= len(labels_by_column[sample_type_idx]) 
                   for sample_type_idx in range(num_sample_types)):
                break
            
            if table_idx == len(doc.tables) - 1:
                if any(label_index_by_sample_type[sample_type_idx] < len(labels_by_column[sample_type_idx]) 
                       for sample_type_idx in range(num_sample_types)):
                    try:
                        doc.add_page_break()
                        new_tbl = deepcopy(original_template_table_xml)
                        doc._body._body.append(new_tbl)
                        new_table = doc.tables[-1]
                        if original_table_style:
                            try:
                                new_table.style = original_table_style
                            except Exception:
                                pass
                    except Exception:
                        break
        
        self._remove_pages_after_last_filled_cell(doc)
        
        return doc
    
    def _fill_template_labels(self, doc, labels_by_column):
        """Fill the template with labels by using existing cells - preserves 100% of template formatting"""
        if not doc.tables:
            return doc
        
        if not labels_by_column:
            return doc
        
        num_columns = len(labels_by_column)
        
        label_index_by_column = [0] * num_columns
        
        filled_tables = []
        
        for table_idx, table in enumerate(doc.tables):
            if len(table.rows) < 1:
                continue
            
            template_rows = len(table.rows)
            template_cols = len(table.rows[0].cells) if table.rows else 0
            
            if num_columns > template_cols:
                continue
            
            table_was_filled = False
            
            for row_idx in range(template_rows):
                row = table.rows[row_idx]
                
                for col_idx in range(num_columns):
                    if col_idx >= len(row.cells):
                        break
                    
                    cell = row.cells[col_idx]
                    column_labels = labels_by_column[col_idx]
                    
                    if label_index_by_column[col_idx] < len(column_labels):
                        label_text = column_labels[label_index_by_column[col_idx]]
                        label_index_by_column[col_idx] += 1
                        table_was_filled = True
                    else:
                        label_text = ''
                    
                    self._replace_cell_text_preserving_format(cell, label_text)
            
            if table_was_filled:
                filled_tables.append(table_idx)
            
            if all(label_index_by_column[col_idx] >= len(labels_by_column[col_idx]) 
                   for col_idx in range(num_columns)):
                break
        
        self._remove_pages_after_last_filled_cell(doc)
        
        return doc
    
    def generate_quick_labels_avalanche(self, num_transects):
        """Generate all labels for Avalanche project - one complete set per transect
        
        For Avalanche:
        - Each transect gets all sample types
        - yield_sample and forage get 2 labels each
        - All other sample types get 1 label each
        """
        from ..constants import SAMPLE_TYPES
        
        transect_codes = self.generate_unique_transect_codes(num_transects)
        self.save_transect_codes(transect_codes)
        
        all_sample_types = [code for code, _ in SAMPLE_TYPES]
        
        doc = self._load_template()
        
        labels_by_column = []
        total_labels = 0
        
        for sample_type_code in all_sample_types:
            sample_type_display = self.get_sample_type_display(sample_type_code)
            column_labels = []
            
            labels_per_transect = 2 if sample_type_code in ['yield_sample', 'forage'] else 1
            
            for transect_code in transect_codes:
                label_text = self.create_label_text(sample_type_display, transect_code)
                
                for _ in range(labels_per_transect):
                    column_labels.append(label_text)
                    total_labels += 1
            
            labels_by_column.append(column_labels)
        
        if doc.tables:
            if self._template_has_placeholders(doc):
                doc = self._fill_template_with_placeholders(doc, labels_by_column)
            else:
                doc = self._fill_template_labels(doc, labels_by_column)
        else:
            doc = self._create_tables_for_labels(doc, labels_by_column)
        
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer, total_labels
    
    def _create_tables_for_labels(self, doc, labels_by_column):
        """Create tables from scratch for labels"""
        max_rows = max(len(col) for col in labels_by_column) if labels_by_column else 0
        table_count = (len(labels_by_column) + 2) // 3
        
        for table_idx in range(table_count):
            start_col = table_idx * 3
            end_col = min(start_col + 3, len(labels_by_column))
            cols_in_table = end_col - start_col
            
            if table_idx > 0:
                doc.add_page_break()
            
            table = doc.add_table(rows=max_rows, cols=cols_in_table)
            table.style = 'Table Grid'
            
            for col_idx in range(cols_in_table):
                sample_idx = start_col + col_idx
                column_labels = labels_by_column[sample_idx]
                
                for row_idx in range(max_rows):
                    cell = table.rows[row_idx].cells[col_idx]
                    
                    if row_idx < len(column_labels):
                        cell.text = column_labels[row_idx]
                        cell.width = Inches(2.3)
                        
                        for paragraph in cell.paragraphs:
                            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            for run in paragraph.runs:
                                run.font.size = Pt(11)
                                run.font.bold = True
            
            for row in table.rows:
                row.height = Inches(0.85)
        
        return doc
    
    def generate_document_with_table(self):
        """Generate Word document with labels organized by sample type in columns using template"""
        total_labels = len(self.sample_types) * self.labels_per_type
        
        transect_codes = self.generate_unique_transect_codes(total_labels)
        self.save_transect_codes(transect_codes)
        
        doc = self._load_template()
        
        code_index = 0
        labels_by_column = []
        
        for sample_type_code in self.sample_types:
            sample_type_display = self.get_sample_type_display(sample_type_code)
            column_labels = []
            
            for _ in range(self.labels_per_type):
                transect_code = transect_codes[code_index]
                label_text = self.create_label_text(sample_type_display, transect_code)
                column_labels.append(label_text)
                code_index += 1
            
            labels_by_column.append(column_labels)
        
        if doc.tables:
            if self._template_has_placeholders(doc):
                doc = self._fill_template_with_placeholders(doc, labels_by_column)
            else:
                doc = self._fill_template_labels(doc, labels_by_column)
        else:
            doc = self._create_tables_for_labels(doc, labels_by_column)
        
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer, total_labels

