from django.forms.models import ModelForm
from django.forms import HiddenInput, ValidationError, inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Column, Field, Row, Fieldset, HTML, Submit, Div
from django.utils.safestring import mark_safe
from django.conf import settings

from .models import Experiment, SamplePlan, Site, Sample
from . import constants


class ModelFormMixin(ModelForm):
    required_fields = []
    hidden_fields = []
    field_labels = {}
    field_choices = {}
    help_text = {}
    help_text_expanded = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)

            field.required = (field_name in self.required_fields)

            if field_name in self.hidden_fields:
                field.widget = HiddenInput()
            
            if field_name in self.field_labels:
                field.label = self.field_labels[field_name]

            if field_name in self.field_choices:
                field.choices = self.field_choices[field_name]

            if field_name in self.help_text:
                field.help_text = self.help_text[field_name]
            else:
                field.help_text = False

            if field_name in self.help_text_expanded:
                field.help_text_expanded = self.help_text_expanded[field_name]

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            *self.get_primary_layout(),
        )
        self.use_required_attribute = False

    def get_primary_layout(self):
        return []
    
    def clean(self):
        cleaned_data = super().clean()
        error_messages = []  # Accumulate error messages here

        # test all fields in required_fields and generate an error message if not entered.
        for field_name in self.required_fields:
            if not cleaned_data.get(field_name):
                # Some .labels are "None" so using "or (field_name...", replacing "_" and capitalizing first word.
                field_label = (
                    self.fields[field_name].label 
                    or (field_name.replace('_', ' ').capitalize() 
                        if not settings.DEBUG  # Do not replace when in DEBUG mode.
                        else f"{field_name} (DEBUG: field.label is 'None'!)")
                )
                error_messages.append(str(field_label))  # Add the label from the missing field.

        if error_messages:
            # Create an unordered list (<ul>) for the error messages
            error_message_list = "<ul>"
            for message in error_messages:
                error_message_list += f"<li>{message}</li>"
            error_message_list += "</ul>"
            
            error_message = mark_safe(f"Please fill out these required fields: {error_message_list}")
            raise ValidationError(error_message)

        return cleaned_data


def get_submit_layout(helper_layout, kwargs):
        """
        Get a submit button based on create vs edit. For example in a ModelFormMixin subclass...
          def __init__(self, *args, **kwargs):
             super().__init__(*args, **kwargs)
             self.helper.layout = get_submit_layout(self.helper.layout, kwargs)
        """
        layout = None
        if 'instance' in kwargs:
            creating = kwargs['instance'] is None
            if creating:
                layout = Submit('submit', 'Create')
            else:
                layout = Submit('submit', 'Save')
        if layout:
            helper_layout.append(layout)
        return helper_layout


class ExperimentForm(ModelFormMixin):
    """
    Parent form for SamplePlanForm.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  use form tags in template to combine with child form
        self.helper.form_tag = False

    class Meta:
        model = Experiment
        fields = constants.FORM_FIELDS_EXPERIMENT
    
    required_fields = constants.FORM_FIELDS_EXPERIMENT_REQUIRED
    field_labels = constants.FORM_FIELDS_EXPERIMENT_LABELS
    
    def get_primary_layout(self):
        return [
            Fieldset(
                'Experiment',
                Row(
                    Column(
                        Row(constants.FIELD_NAME),
                        Row(constants.FIELD_ABBREVIATION, css_class='form-control-width-medium'),
                        Row(
                            Column(constants.FIELD_FROM_YEAR, css_class='form-control-width-medium'),
                            Column(constants.FIELD_TO_YEAR, css_class='form-control-width-medium'),
                        ),
                        Row(constants.FIELD_LEADER),
                        Row(constants.FIELD_COMPLETED),
                    ),
                    Column(constants.FIELD_SUMMARY)
                )
            ),
            Fieldset(
                'Sample Plan',
                Row(
                    Column(constants.FIELD_NO_SITES, css_class='form-control-width-medium'),
                    Column(constants.FIELD_DATE_PER_SITE, css_class='form-control-width-medium')
                )
            ),

        ]


class SamplePlanForm(ModelFormMixin):
    """
    Child form for ExperimentForm.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  use form tags in template to combine with parent form
        self.helper.form_tag = False

    class Meta:
        model = SamplePlan
        fields = constants.FORM_FIELDS_SAMPLE_PLAN
    
    field_labels = constants.FORM_FIELDS_SAMPLE_PLAN_LABELS
    hidden_fields = [constants.FIELD_SAMPLE_PLAN_ID]
    
    def get_primary_layout(self):
        return [
            Field(constants.FIELD_SAMPLE_PLAN_ID),
            HTML("<div class='d-none' id='formsets_row_{{ forloop.counter }}'>"),
            Row(
                Column(constants.FIELD_SAMPLE_PLAN_SAMPLE_TYPE, css_class='form-control-width-medium'),
                Column(constants.FIELD_SAMPLE_PLAN_NO_PER_DATE, css_class='form-control-width-medium'),
                Column(constants.FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE, css_class='form-control-width-medium'),
                Column('DELETE', css_class='mt-5'),
                css_class='my-0'
            ),
            HTML('</div>')
        ]

class SiteForm(ModelFormMixin):
    """
    Parent form for SampleForm.

    Plan here is to make formsets form similar to ExperimentForm.
    In this case, the displayed formsets are based on the sample plan for experiment.
    Although, only give one form per date.
    Then if the one form comes in valid to the view, there create the additional samples
    based from the plan.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  use form tags in template to combine with child form
        self.helper.form_tag = False

    class Meta:
        model = Site
        fields = constants.FORM_FIELDS_SITE_CREATE
