from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Row, Submit
from django.conf import settings
from django.forms import (ClearableFileInput,
                          ChoiceField,
                          DateInput, FileField,
                          Form,
                          HiddenInput, ValidationError)
from django.forms.models import ModelForm
from django.utils.safestring import mark_safe

from . import constants
from .models import LookupChoices


class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(FileField):
    """
    For forms to upload multiple files, for example ...
    from django.forms import Form
    class FileFieldForm(Form):
        file_field = MultipleFileField()
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class Html5DateInput(DateInput):
    """
    HTML5 enabled date widget.
    """
    input_type = 'date'


class ModelFormMixin(ModelForm):
    required_fields = []
    hidden_fields = []
    disabled_fields = []
    field_labels = {}
    field_choices = {}
    help_text = {}

    def __init__(self, *args, **kwargs):
        super(ModelFormMixin, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)

            field.required = (field_name in self.required_fields)

            if field_name in self.hidden_fields:
                field.widget = HiddenInput()

            if field_name in self.disabled_fields:
                field.disabled = True

            if field_name in self.field_labels:
                field.label = self.field_labels[field_name]

            if field_name in self.field_choices:
                field.choices = self.field_choices[field_name]

            if field_name in self.help_text:
                field.help_text = self.help_text[field_name]
            else:
                field.help_text = False

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


class LookupChoicesForm(ModelFormMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = get_submit_layout(self.helper.layout, kwargs)

    class Meta:
        model = LookupChoices
        fields = [
            constants.FIELD_FIELD,
            constants.FIELD_ENTRY,
            constants.FIELD_DISPLAY_TXT,
            'organization'
        ]

    required_fields = [
        constants.FIELD_ENTRY,
        constants.FIELD_DISPLAY_TXT
    ]
    hidden_fields = [constants.FIELD_FIELD, 'organization']

    def get_primary_layout(self):

        row = [Field(constants.FIELD_FIELD)]
        if self.instance.id:
            row += Row(
                    Column(
                        Field(
                            constants.FIELD_ENTRY, readonly=True
                        ), css_class='form-control-width-medium'),
                    Column(
                        constants.FIELD_DISPLAY_TXT, css_class='form-control-width-medium'
                    )
                ),
        else:
            row += [
                Field(constants.FIELD_FIELD),
                Row(
                    Column(
                        constants.FIELD_ENTRY, css_class='form-control-width-medium'
                    ),
                    Column(
                        constants.FIELD_DISPLAY_TXT, css_class='form-control-width-medium'
                    )
                ),
            ]
        return row


class StitcherForm(Form):
    choices = [
        (None, '---'),
        (True, 'Approved'),
        (False, 'Dissaprove')
    ]
    approved = ChoiceField(
        choices=choices,
        label="Approve/Dissaprove",
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'approved',
            Submit('submit', 'Submit')
        )
