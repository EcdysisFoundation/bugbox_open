from crispy_forms.layout import Column, Field, Row

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


class MorphospeciesForm(MorphospeciesFormMixin):

    hidden_fields = constants.FORM_FIELDS_MORPHO_HIDDEN

    def get_primary_layout(self):
        return [Field(v) for v in constants.FORM_FIELDS_MORPHO]


class MorphospeciesUpdateForm(MorphospeciesFormMixin):

    hidden_fields = constants.FORM_FIELDS_MORPHO_UPDATE_HIDDEN
    field_labels = constants.FORM_FIELDS_MORPHO_LABELS
    help_text = constants.FORM_MORPHO_HELP_TEXT

    def get_primary_layout(self):
        return [
            Field(constants.FIELD_MORPHO_GBIF_KEY),
            Row(
                Column(constants.FIELD_MORPHO_NAME),
                Column(constants.FIELD_MORPHO_GBIF_CANONICAL_NAME),
                Column(constants.FIELD_MORPHO_GBIF_SCIENTIFIC_NAME),
            ),
            Row(
                Column(constants.FIELD_MORPHO_GBIF_RANK, css_class='form-control-width-medium'),
                Column(constants.FIELD_MORPHO_GBIF_STATUS, css_class='form-control-width-medium'),
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
            Field(constants.FIELD_MORPHO_NOTE)
        ]
