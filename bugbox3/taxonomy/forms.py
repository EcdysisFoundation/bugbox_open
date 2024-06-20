from crispy_forms.layout import Field

from ..core.forms import ModelFormMixin, get_submit_layout
from . import constants
from .models import Morphospecies


class MorphospeciesForm(ModelFormMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = get_submit_layout(self.helper.layout, kwargs)

    class Meta:
        model = Morphospecies
        fields = constants.FORM_FIELDS_MORPHO

    hidden_fields = constants.FORM_FIELDS_MORPHO_HIDDEN
    required_fields = constants.FORM_FIELDS_MORPHO_REQUIRED

    def get_primary_layout(self):
        return [Field(v) for v in constants.FORM_FIELDS_MORPHO]
