from django.forms import ModelForm, IntegerField

from .models import Morphospecies


class MorphospeciesForm(ModelForm):

    class Meta:
        model = Morphospecies
        fields = ('gbif_key',)

    gbif_key = IntegerField(required=False)
