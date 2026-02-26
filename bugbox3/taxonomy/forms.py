from crispy_forms.layout import HTML, Column, Field, Row
from django.forms import (
    CharField,
    ChoiceField,
    Form,
    IntegerField,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    SelectMultiple,
    Textarea,
    TextInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.html import escape

from ..core.forms import ModelFormMixin, get_submit_layout
from ..core.models import LookupChoices
from . import constants
from .constants import ADULT_HABITAT_CHOICES, CAT_LIFE_STAGE_ADULT, CAT_LIFE_STAGE_YOUNG, YOUNG_HABITAT_CHOICES
from .models import FunctionalGroup, Morphospecies


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

    young_habitat = ChoiceField(
        choices=YOUNG_HABITAT_CHOICES,
        label='Young',
        required=False,
    )
    adult_habitat = ChoiceField(
        choices=ADULT_HABITAT_CHOICES,
        label='Adult',
        required=False,
    )
    functional_groups = ModelMultipleChoiceField(
        queryset=FunctionalGroup.objects.exclude(
            category__in=[CAT_LIFE_STAGE_YOUNG, CAT_LIFE_STAGE_ADULT]
        ),
        widget=CheckboxSelectMultiple,
        required=False,
        label='Functional groups',
    )

    class Meta(MorphospeciesFormMixin.Meta):
        fields = constants.FORM_FIELDS_MORPHO + (constants.FIELD_MORPHO_FUNCTIONAL_GROUPS,)

    def __init__(self, *args, **kwargs):
        self._fg_phytophagous = kwargs.pop('functional_groups_phytophagous', [])
        self._fg_zoophagous = kwargs.pop('functional_groups_zoophagous', [])
        self._fg_other = kwargs.pop('functional_groups_other', [])
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            fg_codes = set(
                self.instance.functional_groups.values_list('code', flat=True)
            )
            if 'young_terrestrial' in fg_codes:
                self.fields['young_habitat'].initial = 'young_terrestrial'
            elif 'young_aquatic' in fg_codes:
                self.fields['young_habitat'].initial = 'young_aquatic'
            if 'adult_terrestrial' in fg_codes:
                self.fields['adult_habitat'].initial = 'adult_terrestrial'
            elif 'adult_aquatic' in fg_codes:
                self.fields['adult_habitat'].initial = 'adult_aquatic'

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
            Field(constants.FIELD_MORPHO_TAGS),
            HTML('<h5 class="mb-2">Functional groups</h5>'),
            Row(
                Column('young_habitat'),
                Column('adult_habitat'),
            ),
            self._build_functional_groups_html(),
        ]

    def _build_functional_groups_html(self):
        """Build functional groups checkboxes for layout."""
        selected_ids = set()
        if self.instance and self.instance.pk:
            selected_ids = set(
                self.instance.functional_groups.values_list('id', flat=True)
            )
        parts = ['<div class="mb-3">']
        if self._fg_phytophagous:
            parts.append('<h6 class="mb-2">Phytophagous</h6><div class="mb-2">')
            for fg in self._fg_phytophagous:
                parts.append(self._fg_checkbox(fg, selected_ids))
            parts.append('</div>')
        if self._fg_zoophagous:
            parts.append('<hr class="my-3 border-secondary"/><h6 class="mb-2 mt-2">Zoophagous</h6><div class="mb-2">')
            for fg in self._fg_zoophagous:
                parts.append(self._fg_checkbox(fg, selected_ids))
            parts.append('</div>')
        if self._fg_other:
            parts.append('<hr class="my-3 border-secondary"/><h6 class="mb-2 mt-2">Other</h6><div class="mb-2">')
            for fg in self._fg_other:
                parts.append(self._fg_checkbox(fg, selected_ids))
            parts.append('</div>')
        parts.append('</div>')
        return HTML(''.join(parts))

    def _fg_checkbox(self, fg, selected_ids):
        checked = ' checked' if fg.id in selected_ids else ''
        return (
            f'<div class="form-check">'
            f'<input class="form-check-input" type="checkbox" name="functional_groups" '
            f'value="{fg.id}" id="fg_{fg.id}"{checked}>'
            f'<label class="form-check-label" for="fg_{fg.id}" '
            f'data-bs-toggle="tooltip" data-bs-title="{escape(fg.description)}">'
            f'{escape(fg.display_name)}</label></div>'
        )

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if not commit:
            return instance
        life_stage_fgs = FunctionalGroup.objects.filter(
            category__in=[CAT_LIFE_STAGE_YOUNG, CAT_LIFE_STAGE_ADULT]
        )
        instance.functional_groups.remove(*life_stage_fgs)
        young = self.cleaned_data.get('young_habitat')
        adult = self.cleaned_data.get('adult_habitat')
        if young:
            instance.functional_groups.add(
                FunctionalGroup.objects.get(code=young)
            )
        if adult:
            instance.functional_groups.add(
                FunctionalGroup.objects.get(code=adult)
            )
        return instance


class MorphospeciesCombineForm(Form):

    combine_to_id = IntegerField(
        required=False)
