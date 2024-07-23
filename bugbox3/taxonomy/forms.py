from crispy_forms.layout import Column, Field, Row
from django.forms import CharField, IntegerField, Textarea, TextInput, Form

from ..core.forms import ModelFormMixin, get_submit_layout
from . import constants
from .models import Morphospecies


class MorphospeciesFormMixin(ModelFormMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = get_submit_layout(self.helper.layout, kwargs)

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
            Field(constants.FIELD_MORPHO_IMAGE)
        ]


class MorphospeciesCombineForm(Form):

    combine_to_id = IntegerField(
        required=False)
