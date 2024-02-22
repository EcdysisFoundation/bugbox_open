from django.forms.models import ModelForm
from django.forms import HiddenInput, ValidationError, inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Column, Field, Row, Fieldset, HTML, Submit
from django.utils.safestring import mark_safe
from django.conf import settings

from .models import Experiment, SamplePlan
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

        #  if there is not an existing instance, then we are creating a new one.
        if 'instance' in kwargs:
            # see if it is empty or not
            self.is_creating = kwargs['instance'] is None
        else:
            # handle case were instance does not apply
            self.is_creating = None 

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            *self.get_layout(),
            self.get_submit_layout(),
        )
        self.use_required_attribute = False

    def get_primary_layout(self):
        return []
    
    def get_submit_layout(self):
        layout = None

        if self.is_creating is not None:
            if self.is_creating:
                layout = Submit('submit', 'Create')
            else:
                layout = Submit('submit', 'Save')
    
        return layout
    
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

class FormSetHelperMixin(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
                *self.get_layout(),
            )
        self.render_required_fields = True


class SamplePlanFormSetHelper(FormSetHelperMixin):
    def get_layout(self):
            return [
                Row(
                    Column(constants.FIELD_SAMPLE_PLAN_SAMPLE_TYPE, css_class='form-control-width-medium'),
                    Column(constants.FIELD_SAMPLE_PLAN_NO_PER_DATE, css_class='form-control-width-medium'),
                    Column(constants.FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE, css_class='form-control-width-medium')
                )
            ]

class ExperimentForm(ModelFormMixin):
    required_fields = [constants.FIELD_NAME, constants.FIELD_FROM_YEAR, constants.FIELD_TO_YEAR,
                       constants.FIELD_LEADER, 
                       #  constants.FIELD_NO_SITES, constants.FIELD_DATE_PER_SITE
                       ]
    field_labels = {
        constants.FIELD_NAME: 'Experiment Name',
    }
    
    
    def get_layout(self):
        return [
            Fieldset(
                'Experiment',
                Field(constants.FIELD_NAME),
                Row(
                    Column(constants.FIELD_FROM_YEAR, css_class='form-control-width-medium'),
                    Column(constants.FIELD_TO_YEAR, css_class='form-control-width-medium'),
                ),
                Field(constants.FIELD_LEADER),
                css_class='card-body'
            ),
            Fieldset(
                'Experiment Setup',
                HTML('<p>placeholder</p>')
            ),
            Fieldset(
                '',
                Column(constants.FIELD_COMPLETED),
                Column(constants.FIELD_SUMMARY)
            )
        ]


class ExperimentForm2(ModelFormMixin):

    class Meta:
        model = Experiment
        fields = constants.FORM_FIELDS_EXPERIMENT

    def get_layout(self):
        return [
            Fieldset(
                'Experiment',
                Field(constants.FIELD_NAME),
                Row(
                    Column(constants.FIELD_FROM_YEAR, css_class='form-control-width-medium'),
                    Column(constants.FIELD_TO_YEAR, css_class='form-control-width-medium'),
                ),
                Field(constants.FIELD_LEADER),
                css_class='card-body'
            ),
            Fieldset(
                'Experiment Setup',
                HTML('<p>placeholder</p>')
            ),
            Fieldset(
                '',
                Column(constants.FIELD_COMPLETED),
                Column(constants.FIELD_SUMMARY)
            )
        ]


class SamplePlanForm(ModelFormMixin):

    class Meta:
        model = SamplePlan
        fields = constants.FORM_FIELDS_SAMPLE_PLAN
    
    def get_layout(self):
        return [
            Fieldset(
                Row(
                    Column(constants.FIELD_SAMPLE_PLAN_SAMPLE_TYPE, css_class='form-control-width-medium'),
                    Column(constants.FIELD_SAMPLE_PLAN_NO_PER_DATE, css_class='form-control-width-medium'),
                    Column(constants.FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE, css_class='form-control-width-medium')
                )
            )
        ]


SamplePlanFormSet = inlineformset_factory(
    Experiment, SamplePlan, form=SamplePlanForm,
    extra=1, can_delete=True, can_delete_extra=True
)

class ExperimentForm3(ModelForm):

    class Meta:
        model = Experiment
        fields = constants.FORM_FIELDS_EXPERIMENT


class SamplePlanForm3(ModelForm):

    class Meta:
        model = SamplePlan
        fields = constants.FORM_FIELDS_SAMPLE_PLAN

SamplePlanFormSet3 = inlineformset_factory(
    Experiment, SamplePlan, form=SamplePlanForm3,
    extra=2)
