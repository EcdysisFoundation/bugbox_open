from crispy_forms.layout import Column, Field, Row
from django.core.exceptions import ValidationError
from django.forms import CharField, Form, IntegerField, MultipleChoiceField, SelectMultiple, Textarea, TextInput

from ..core.forms import ModelFormMixin, get_submit_layout
from ..core.models import LookupChoices
from . import constants
from .models import Morphospecies


class MorphospeciesFormMixin(ModelFormMixin):

    def __init__(self, *args, **kwargs):
        self.org_id = kwargs.pop('org_id', None)
        super().__init__(*args, **kwargs)
        self.helper.layout = get_submit_layout(self.helper.layout, kwargs)
        if self.org_id and constants.FIELD_MORPHO_TAGS in self.fields:
            self.fields[
                constants.FIELD_MORPHO_TAGS
            ].choices = lambda: LookupChoices.objects.get_field_choices(
                self.org_id, constants.FIELD_MORPHO_TAGS_LOOKUP)

    class Meta:
        model = Morphospecies
        fields = constants.FORM_FIELDS_MORPHO

    required_fields = constants.FORM_FIELDS_MORPHO_REQUIRED
    field_labels = constants.FORM_FIELDS_MORPHO_LABELS
    help_text = constants.FORM_MORPHO_HELP_TEXT

    gbif_canonical_name = CharField(widget=TextInput(attrs={'readonly': 'readonly'}))
    note = CharField(
        widget=Textarea
    )
    tags = MultipleChoiceField(
        widget=SelectMultiple,
        required=False
    )

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', [])
        if not tags or not self.org_id:
            return tags
        
        valid_choices = LookupChoices.objects.get_field_choices(
            self.org_id, constants.FIELD_MORPHO_TAGS_LOOKUP)
        valid_tag_values = [choice[0] for choice in valid_choices if choice[0]]
        
        valid_tags = [tag for tag in tags if tag in valid_tag_values]
        
        if len(valid_tags) < len(tags):
            pass
        return valid_tags


class MorphospeciesForm(MorphospeciesFormMixin):

    hidden_fields = constants.FORM_FIELDS_MORPHO_HIDDEN

    def get_primary_layout(self):
        return [Field(v) for v in constants.FORM_FIELDS_MORPHO]


class MorphospeciesUpdateForm(MorphospeciesFormMixin):

    hidden_fields = constants.FORM_FIELDS_MORPHO_UPDATE_HIDDEN

    def get_primary_layout(self):
        return [
            Field(constants.FIELD_MORPHO_GBIF_KEY),
            Row(
                Column(constants.FIELD_MORPHO_NAME),
                Column(constants.FIELD_MORPHO_GBIF_CANONICAL_NAME),
                Column(constants.FIELD_MORPHO_GBIF_SCIENTIFIC_NAME),
            ),
            Row(
                Column(constants.FIELD_MORPHO_GBIF_RANK),
                Column(constants.FIELD_MORPHO_GBIF_STATUS),
                Column(constants.FIELD_MORPHO_GBIF_PHYLUM),
            ),
            Row(
                Column(constants.FIELD_MORPHO_GBIF_CLASS),
                Column(constants.FIELD_MORPHO_GBIF_ORDER),
                Column(constants.FIELD_MORPHO_GBIF_FAMILY),
            ),
            Row(
                Column(constants.FIELD_MORPHO_SUBFAMILY),
                Column(constants.FIELD_MORPHO_GBIF_GENUS),
                Column(constants.FIELD_MORPHO_GBIF_SPECIES),
            ),
            Field(constants.FIELD_MORPHO_NOTE),
            Field(constants.FIELD_MORPHO_IMAGE),
            Field(constants.FIELD_MORPHO_EXCLUDE),
            Field(constants.FIELD_MORPHO_TAGS)
        ]


class MorphospeciesCombineForm(Form):

    combine_to_id = IntegerField(
        required=False)
