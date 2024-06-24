from crispy_forms.layout import HTML, Column, Field, Fieldset, Row
from django.forms import CharField, ChoiceField, DateField, Form, IntegerField, Select, Textarea

from ..core.forms import Html5DateInput, ModelFormMixin, MultipleFileField, get_submit_layout
from . import constants
from .models import Experiment, Sample, SamplePlan, Site, SiteVisit, Specimen


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
    Parent form for SiteVisit
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  use form tags in template to combine with child form
        self.helper.form_tag = False

    class Meta:
        model = Site
        fields = constants.FORM_FIELDS_SITE

    required_fields = [
        constants.FIELD_SITE_SITE_NAME,
        constants.FIELD_SITE_LATITUDE,
        constants.FIELD_SITE_LONGITUDE,
        constants.FIELD_SITE_TREATMENT,
        constants.FIELD_SITE_HABITAT_TYPE
    ]

    hidden_fields = [
        constants.FIELD_SITE_EXPERIMENT_ID
    ]

    def get_primary_layout(self):
        return [
            Field(constants.FIELD_SITE_EXPERIMENT_ID),
            Field(constants.FIELD_SITE_SITE_NAME, css_class='form-control-width-medium'),
            Row(
                Column(constants.FIELD_SITE_LATITUDE, css_class='form-control-width-medium'),
                Column(constants.FIELD_SITE_LONGITUDE, css_class='form-control-width-medium'),
            ),
            Row(
                Column(constants.FIELD_SITE_TREATMENT, css_class='form-control-width-medium'),
                Column(constants.FIELD_SITE_HABITAT_TYPE, css_class='form-control-width-medium'),
            )
        ]

    treatment = ChoiceField(
        widget=Select,
        choices=constants.SITE_TREATMENT_CHOICES_W_BLANK
    )

    habitat_type = ChoiceField(
        widget=Select,
        choices=constants.SITE_HABITAT_TYPE_CHOICES_W_BLANK
    )


class SiteVisitForm(ModelFormMixin):
    """
    Child form for SiteForm
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  use form tags in template to combine with parent form
        self.helper.form_tag = False

    class Meta:
        model = SiteVisit
        fields = constants.FORM_FIELDS_SITE_VISIT

    hidden_fields = [constants.FIELD_SITE_VISIT_ID]

    def get_primary_layout(self):
        return [
            Field(constants.FIELD_SITE_VISIT_ID),
            HTML("<div class='d-none' id='formsets_row_{{ forloop.counter }}'>"),
            Row(
                Column(constants.FIELD_SITE_VISIT_DATE, css_class='form-control-width-medium'),
                Column('DELETE', css_class='mt-5'),
                css_class='my-0'
            ),
            HTML('</div>')
        ]

    visit_date = DateField(
        widget=Html5DateInput
    )


class SampleForm(ModelFormMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = get_submit_layout(self.helper.layout, kwargs)

    class Meta:
        model = Sample
        fields = constants.FORM_FIELDS_SAMPLE

    def get_primary_layout(self):
        return [
            Field(constants.FIELD_SAMPLE_TYPE, css_class='form-control-width-medium'),
            Field(constants.FIELD_SAMPLE_NAME_NO, css_class='form-control-width-medium'),
            Field(constants.FIELD_SAMPLE_IMAGE),
            Field(constants.FIELD_SAMPLE_NOTES),
            Field(constants.FIELD_SAMPLE_COMPLETED),
        ]

    notes = CharField(
        widget=Textarea
    )


class NewSpecimenImageForm(Form):

    image = MultipleFileField()


class SpecimenViewForm(Form):

    image_files = MultipleFileField(required=False)
    primary_picker = IntegerField(required=False)
    delete_picker = IntegerField(required=False)
    determin_picker = IntegerField(required=False)


class SpecimenUpdateForm(ModelFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = get_submit_layout(self.helper.layout, kwargs)

    class Meta:
        model = Specimen
        fields = constants.FORM_FIELDS_SPECIMEN

    hidden_fields = constants.FORM_FIELDS_SPECIMEN_HIDDEN
    field_labels = constants.FORM_FIELDS_SPECIMEN_LABELS

    def get_primary_layout(self):
        return [
            Field(constants.FIELD_SPECIMEN_CLASSIFICATION),
            Field(constants.FIELD_SPECIMEN_ACCEPTANCE),
            Row(
                Column(constants.FIELD_SPECIMEN_PARTIAL_COUNT, css_class='form-control-width-medium'),
                Column(constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER, css_class='form-control-width-medium'),
                Column(constants.FIELD_SPECIMEN_ARCHIVAL_PRESERVATION, css_class='form-control-width-medium'),
                Column(constants.FIELD_SPECIMEN_ARCHIVAL_STORED, css_class='form-control-width-medium'),
            ),
        ]
