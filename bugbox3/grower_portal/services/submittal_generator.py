from io import BytesIO
from openpyxl import load_workbook
from django.db.models import Q

from ..models import LabelGeneration, GrowerApplication
from bugbox3.core.models import PublicSiteContent
from ..constants import (
    SUBMITTAL_TEMPLATE_SLUG,
    SUBMITTAL_TEST_ID_SOIL,
    SUBMITTAL_TEST_ID_SH,
    SUBMITTAL_SH_START_DEPTH,
    SUBMITTAL_SH_END_DEPTH,
    SUBMITTAL_SH_INCHES_START,
    SUBMITTAL_SH_INCHES_END,
)


class SubmittalFormGenerator:
    
    DEPTH_RANGES = [
        (0, 5),
        (5, 10),
        (10, 15),
        (15, 30),
        (30, 60)
    ]
    
    def __init__(self, cluster_number, year):
        self.cluster_number = cluster_number
        self.year = year
        self.transect_codes = []
        self.grower_names = {}
    
    def validate_cluster(self):
        return LabelGeneration.objects.filter(
            cluster_number=self.cluster_number,
            year=self.year
        ).exists()
    
    def get_latest_label_generation(self):
        label_generation = LabelGeneration.objects.filter(
            cluster_number=self.cluster_number,
            year=self.year
        ).order_by('-generated_at').first()
        
        if label_generation:
            self.transect_codes = label_generation.transect_codes_generated
        
        return label_generation
    
    def get_grower_applications(self):
        """
        Find applications by matching transect codes from label generation.
        """
        if not self.transect_codes:
            return {}
        
        query = Q()
        for transect_code in self.transect_codes:
            query |= (
                Q(transect_code_1=transect_code) |
                Q(transect_code_2=transect_code) |
                Q(transect_code_3=transect_code) |
                Q(transect_code_4=transect_code)
            )
        
        applications = GrowerApplication.objects.filter(query).select_related('grower').distinct()
        
        for app in applications:
            grower_name = app.grower.name if hasattr(app.grower, 'name') and app.grower.name else app.grower.username
            
            for i in range(1, 5):
                transect_code = getattr(app, f'transect_code_{i}', None)
                if transect_code and transect_code in self.transect_codes:
                    self.grower_names[transect_code] = grower_name
        
        return self.grower_names
    
    def _load_template(self):
        try:
            template_content = PublicSiteContent.objects.get(title=SUBMITTAL_TEMPLATE_SLUG)
            
            if not template_content.file:
                raise ValueError(
                    f"Submittal template '{SUBMITTAL_TEMPLATE_SLUG}' found in PublicSiteContent but file is missing. Please upload it in Django Admin"
                )
            
            with template_content.file.open('rb') as file:
                file_content = file.read()
                file_buffer = BytesIO(file_content)
                try:
                    return load_workbook(file_buffer)
                except Exception as e:
                    error_msg = str(e)
                    if 'not a valid' in error_msg.lower() or 'cannot open' in error_msg.lower():
                        raise ValueError(
                            f"Template file '{SUBMITTAL_TEMPLATE_SLUG}' could not be loaded. Please ensure your template is a valid Excel file (.xlsx). "
                            f"Original error: {error_msg}"
                        ) from e
                    else:
                        raise
        
        except PublicSiteContent.DoesNotExist:
            raise ValueError(
                f"Submittal template '{SUBMITTAL_TEMPLATE_SLUG}' not found in PublicSiteContent. "
                f"Please upload the template file to PublicSiteContent with title '{SUBMITTAL_TEMPLATE_SLUG}' in Django Admin"
            )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(
                f"Error loading submittal template: {str(e)}"
            ) from e
    
    def _cm_to_inches(self, cm):
        return round(cm / 2.54)
    
    def _populate_soil_sheet(self, workbook, transect_codes, grower_names):
        try:
            ws = workbook['Soil']
        except KeyError:
            raise ValueError("The Excel template is missing the 'Soil' sheet. Please check the template file.")
        
        header_row = 6
        headers = {}
        for col_idx, cell in enumerate(ws[header_row], start=1):
            if cell.value:
                header_text = str(cell.value).strip().lower()
                headers[header_text] = col_idx
        
        col_test_id = headers.get('test id')
        col_grower = headers.get('grower')
        col_field = headers.get('field')
        col_sample_id_1 = headers.get('sample id 1')
        col_start_depth = headers.get('start depth')
        col_end_depth = headers.get('end depth')
        col_inches_start = headers.get('inches')
        col_inches_end = col_inches_start + 1 if col_inches_start else None
        
        required_columns = {
            'test id': col_test_id,
            'grower': col_grower,
            'field': col_field,
            'sample id 1': col_sample_id_1,
            'start depth': col_start_depth,
            'end depth': col_end_depth,
            'inches': col_inches_start,
        }
        missing = [name for name, col in required_columns.items() if col is None]
        if missing:
            raise ValueError(
                f"Error in Soil sheet: Could not find required columns in row 6: {', '.join(missing)}. "
                f"Found columns: {list(headers.keys())}"
            )
        
        current_row = header_row + 1
        
        for transect_code in transect_codes:
            grower_name = grower_names.get(transect_code, '')
            
            for start_depth, end_depth in self.DEPTH_RANGES:
                inches_start = self._cm_to_inches(start_depth)
                inches_end = self._cm_to_inches(end_depth)
                
                ws.cell(row=current_row, column=col_test_id, value=SUBMITTAL_TEST_ID_SOIL)
                ws.cell(row=current_row, column=col_grower, value=self.cluster_number)
                ws.cell(row=current_row, column=col_field, value=grower_name)
                ws.cell(row=current_row, column=col_sample_id_1, value=transect_code)
                ws.cell(row=current_row, column=col_start_depth, value=start_depth)
                ws.cell(row=current_row, column=col_end_depth, value=end_depth)
                ws.cell(row=current_row, column=col_inches_start, value=inches_start)
                ws.cell(row=current_row, column=col_inches_end, value=inches_end)
                
                current_row += 1
        
        return workbook
    
    def _populate_sh_sheet(self, workbook, transect_codes, grower_names):
        try:
            ws = workbook['SH']
        except KeyError:
            raise ValueError("The Excel template is missing the 'SH' sheet. Please check the template file.")
        
        header_row = 6
        headers = {}
        for col_idx, cell in enumerate(ws[header_row], start=1):
            if cell.value:
                header_text = str(cell.value).strip().lower()
                headers[header_text] = col_idx
        
        col_test_id = headers.get('test id')
        col_grower = headers.get('grower')
        col_field = headers.get('field')
        col_sample_id_1 = headers.get('sample id 1')
        col_start_depth = headers.get('start depth')
        col_end_depth = headers.get('end depth')
        col_inches_start = headers.get('inches')
        col_inches_end = col_inches_start + 1 if col_inches_start else None
        
        required_columns = {
            'test id': col_test_id,
            'grower': col_grower,
            'field': col_field,
            'sample id 1': col_sample_id_1,
            'start depth': col_start_depth,
            'end depth': col_end_depth,
            'inches': col_inches_start,
        }
        missing = [name for name, col in required_columns.items() if col is None]
        if missing:
            raise ValueError(
                f"Error in SH sheet: Could not find required columns in row 6: {', '.join(missing)}. "
                f"Found columns: {list(headers.keys())}"
            )
        
        current_row = header_row + 1
        
        for transect_code in transect_codes:
            grower_name = grower_names.get(transect_code, '')
            
            ws.cell(row=current_row, column=col_test_id, value=SUBMITTAL_TEST_ID_SH)
            ws.cell(row=current_row, column=col_grower, value=self.cluster_number)
            ws.cell(row=current_row, column=col_field, value=grower_name)
            ws.cell(row=current_row, column=col_sample_id_1, value=transect_code)
            ws.cell(row=current_row, column=col_start_depth, value=SUBMITTAL_SH_START_DEPTH)
            ws.cell(row=current_row, column=col_end_depth, value=SUBMITTAL_SH_END_DEPTH)
            ws.cell(row=current_row, column=col_inches_start, value=SUBMITTAL_SH_INCHES_START)
            ws.cell(row=current_row, column=col_inches_end, value=SUBMITTAL_SH_INCHES_END)
            
            current_row += 1
        
        return workbook
    
    def generate_submittal_form(self):
        if not self.validate_cluster():
            raise ValueError(
                f"No label generation found for cluster {self.cluster_number} in year {self.year}"
            )
        
        label_gen = self.get_latest_label_generation()
        if not label_gen:
            raise ValueError(
                f"Could not retrieve label generation for cluster {self.cluster_number} in year {self.year}"
            )
        
        grower_names = self.get_grower_applications()
        
        workbook = self._load_template()
        
        workbook = self._populate_soil_sheet(workbook, self.transect_codes, grower_names)
        workbook = self._populate_sh_sheet(workbook, self.transect_codes, grower_names)
        
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        
        filename = f"Submittal_Form_{self.cluster_number}_{self.year}.xlsx"
        
        return buffer, filename

