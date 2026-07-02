from crispy_forms.layout import HTML, Column, Field, Layout, Row

from django.core.exceptions import ValidationError

from django.forms import (

    BooleanField,

    CharField,

    ChoiceField,

    Form,

    IntegerField,

    MultipleChoiceField,

    SelectMultiple,

    Textarea,

    TextInput,

)

from django.utils.html import escape



from ..core.forms import ModelFormMixin, get_submit_layout

from ..core.models import LookupChoices

from . import constants

from .constants import ADULT_HABITAT_CHOICES, YOUNG_HABITAT_CHOICES

from .functional_group_config import (
    FUNCTIONAL_GROUP_FORM_INTRO,
    FUNCTIONAL_GROUP_UI_SECTIONS,
    GROWER_ECOLOGICAL_ROLE_HELP,
    GROWER_ECOLOGICAL_ROLE_MAPPING,
    LIFE_STAGE_FORM_HELP,
    OTHER_SECTION_HELP,
    PARENT_SUBTYPE_SECTION_HELP,
)

from .functional_group_form import traits_from_checkboxes

from .functional_group_validation import validate_functional_group_traits

from .functional_groups import get_active_traits_for_morphospecies, set_active_traits_for_morphospecies

from .models import FunctionalGroup, Morphospecies



FG_TRAIT_FIELD_PREFIX = 'fg_trait_'





def functional_group_trait_field_name(code: str) -> str:

    return f'{FG_TRAIT_FIELD_PREFIX}{code}'





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

    taxonomy_reviewed = BooleanField(

        required=False,

        label=constants.FORM_FIELDS_MORPHO_LABELS[constants.FIELD_MORPHO_TAXONOMY_REVIEWED],

    )



    class Meta(MorphospeciesFormMixin.Meta):

        fields = constants.FORM_FIELDS_MORPHO + (

            constants.FIELD_MORPHO_TAXONOMY_REVIEWED,

        )



    def __init__(self, *args, **kwargs):

        self._taxonomy_reviewer_user = kwargs.pop('taxonomy_reviewer_user', False)

        kwargs.pop('functional_groups_phytophagous', None)

        kwargs.pop('functional_groups_zoophagous', None)

        kwargs.pop('functional_groups_other', None)

        self._functional_groups_by_code = {
            fg.code: fg for fg in FunctionalGroup.objects.all()
        }

        super().__init__(*args, **kwargs)

        if not self._taxonomy_reviewer_user:

            self.fields.pop(constants.FIELD_MORPHO_TAXONOMY_REVIEWED, None)



        existing_traits = {}

        if self.instance and self.instance.pk:

            existing_traits = get_active_traits_for_morphospecies(self.instance)

            if existing_traits.get('young_terrestrial'):

                self.fields['young_habitat'].initial = 'young_terrestrial'

            elif existing_traits.get('young_aquatic'):

                self.fields['young_habitat'].initial = 'young_aquatic'

            if existing_traits.get('adult_terrestrial'):

                self.fields['adult_habitat'].initial = 'adult_terrestrial'

            elif existing_traits.get('adult_aquatic'):

                self.fields['adult_habitat'].initial = 'adult_aquatic'



        for section in FUNCTIONAL_GROUP_UI_SECTIONS:

            if section['key'] == 'life_stage':

                continue

            codes = []

            if section['parent_code']:

                codes.append(section['parent_code'])

            codes.extend(section['subtype_codes'])

            for code in codes:

                field_name = functional_group_trait_field_name(code)

                fg = self._functional_groups_by_code.get(code)

                label = fg.display_name if fg else code

                self.fields[field_name] = BooleanField(

                    required=False,

                    label=label,

                )

                if existing_traits.get(code):

                    self.fields[field_name].initial = True

        self.helper.layout = get_submit_layout(
            Layout(*self.get_primary_layout()),
            {'instance': self.instance},
        )

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

            *(

                [Field(constants.FIELD_MORPHO_TAXONOMY_REVIEWED)]

                if self._taxonomy_reviewer_user

                else []

            ),

            Field(constants.FIELD_MORPHO_NOTE),

            Field(constants.FIELD_MORPHO_IMAGE),

            Field(constants.FIELD_MORPHO_EXCLUDE),

            Field(constants.FIELD_MORPHO_TAGS),

            HTML('<h5 class="mb-2">Functional groups</h5>'),

            HTML(f'<p class="text-muted small mb-2">{escape(FUNCTIONAL_GROUP_FORM_INTRO)}</p>'),

            HTML(self._build_grower_ecological_roles_html()),

            HTML('<h6 class="mb-2">Life stage</h6>'),

            HTML(f'<p class="text-muted small mb-2">{escape(LIFE_STAGE_FORM_HELP)}</p>'),

            Row(

                Column('young_habitat'),

                Column('adult_habitat'),

            ),

            self._build_functional_groups_html(),

        ]



    def _build_grower_ecological_roles_html(self) -> str:
        rows = ''.join(
            f'<li><span class="fw-semibold">{escape(role)}</span> = {escape(traits)}</li>'
            for role, traits in GROWER_ECOLOGICAL_ROLE_MAPPING
        )
        return (
            f'<div class="alert alert-light border small mb-3">'
            f'<div class="fw-semibold mb-1">Grower ecological roles</div>'
            f'<p class="text-muted mb-2">{escape(GROWER_ECOLOGICAL_ROLE_HELP)}</p>'
            f'<ul class="mb-0 ps-3">{rows}</ul>'
            f'</div>'
        )

    def _fg_checkbox_html(
        self,
        *,
        field_name: str,
        code: str,
        is_checked: bool,
        extra_class: str = '',
        col_class: str = 'col-md-6 col-lg-4',
    ) -> str:
        fg = self._functional_groups_by_code.get(code)
        description = escape(fg.description) if fg else ''
        label = escape(fg.display_name if fg else code)
        checked = ' checked' if is_checked else ''
        return (
            f'<div class="{col_class} fg-trait-field" data-fg-code="{escape(code)}">'
            f'<div class="fg-trait-card h-100">'
            f'<div class="form-check mb-0">'
            f'<input type="checkbox" class="form-check-input fg-trait-checkbox {extra_class}" '
            f'name="{field_name}" id="id_{field_name}" value="on"{checked}>'
            f'<label class="form-check-label fw-semibold" for="id_{field_name}">{label}</label>'
            f'</div>'
            f'<p class="fg-trait-description small text-muted mb-0">{description}</p>'
            f'</div>'
            f'</div>'
        )

    def _is_trait_checked(self, field_name: str) -> bool:
        if field_name not in self.fields:
            return False
        value = self[field_name].value()
        if value in (True, 'on', 'true', '1', 1):
            return True
        if value in (False, None, '', 'off', 'false', '0', 0):
            return False
        return bool(value)

    def _build_parent_subtype_section_html(self, section: dict) -> str:
        parent_code = section['parent_code']
        subtype_codes = section['subtype_codes']
        section_key = section['key']
        title = escape(section['title'])
        help_text = escape(PARENT_SUBTYPE_SECTION_HELP.get(section_key, ''))
        parent_field = functional_group_trait_field_name(parent_code)

        parts = [
            f'<div class="card mb-3 fg-section fg-section-parent" '
            f'data-fg-section="{escape(section_key)}" data-parent-code="{escape(parent_code)}">',
            '<div class="card-header d-flex justify-content-between align-items-center py-2">',
            f'<span class="fw-semibold">{title}</span>',
            '<button type="button" class="btn btn-outline-secondary btn-sm fg-clear-section">'
            'Clear</button>',
            '</div>',
            '<div class="card-body">',
            f'<p class="small text-muted mb-3">{help_text}</p>',
            '<div class="fg-parent-row mb-3">',
            self._fg_checkbox_html(
                field_name=parent_field,
                code=parent_code,
                is_checked=self._is_trait_checked(parent_field),
                extra_class='fg-parent-checkbox',
                col_class='col-12',
            ),
            '</div>',
            '<div class="small text-muted mb-2">Feeding modes</div>',
            '<div class="row g-3 fg-trait-grid">',
        ]

        for code in subtype_codes:
            field_name = functional_group_trait_field_name(code)
            if field_name not in self.fields:
                continue
            parts.append(
                self._fg_checkbox_html(
                    field_name=field_name,
                    code=code,
                    is_checked=self._is_trait_checked(field_name),
                    extra_class='fg-subtype-checkbox',
                )
            )

        parts.extend(['</div>', '</div>', '</div>'])
        return ''.join(parts)

    def _build_other_section_html(self, section: dict) -> str:
        title = escape(section['title'])
        help_text = escape(OTHER_SECTION_HELP)
        parts = [
            f'<div class="card mb-3 fg-section fg-section-other" data-fg-section="{escape(section["key"])}">',
            '<div class="card-header py-2">',
            f'<span class="fw-semibold">{title}</span>',
            '</div>',
            '<div class="card-body">',
            f'<p class="small text-muted mb-3">{help_text}</p>',
            '<div class="row g-3">',
        ]
        for code in section['subtype_codes']:
            field_name = functional_group_trait_field_name(code)
            if field_name not in self.fields:
                continue
            parts.append(
                self._fg_checkbox_html(
                    field_name=field_name,
                    code=code,
                    is_checked=self._is_trait_checked(field_name),
                )
            )
        parts.extend(['</div>', '</div>', '</div>'])
        return ''.join(parts)

    def _build_functional_groups_html(self):

        parts = ['<div class="mb-3 functional-group-weights">']

        for section in FUNCTIONAL_GROUP_UI_SECTIONS:

            if section['key'] == 'life_stage':

                continue

            if section['parent_code']:

                parts.append(self._build_parent_subtype_section_html(section))

            else:

                parts.append(self._build_other_section_html(section))

        parts.append('</div>')

        return HTML(''.join(parts))



    def _collect_checked_traits(self) -> dict[str, bool]:

        checked: dict[str, bool] = {}

        for name, value in self.cleaned_data.items():

            if not name.startswith(FG_TRAIT_FIELD_PREFIX):

                continue

            code = name[len(FG_TRAIT_FIELD_PREFIX):]

            checked[code] = bool(value)

        return checked



    def _active_traits_from_form(self) -> dict[str, bool]:

        traits = traits_from_checkboxes(self._collect_checked_traits())

        young = self.cleaned_data.get('young_habitat')

        adult = self.cleaned_data.get('adult_habitat')

        if young:

            traits[young] = True

        if adult:

            traits[adult] = True

        return traits



    def clean(self):

        cleaned_data = super().clean()

        checked = {}

        for name, value in cleaned_data.items():

            if not name.startswith(FG_TRAIT_FIELD_PREFIX):

                continue

            code = name[len(FG_TRAIT_FIELD_PREFIX):]

            checked[code] = bool(value)

        traits = traits_from_checkboxes(checked)

        young = cleaned_data.get('young_habitat')

        adult = cleaned_data.get('adult_habitat')

        if young:

            traits[young] = True

        if adult:

            traits[adult] = True

        try:

            validate_functional_group_traits(traits)

        except ValidationError as exc:

            raise ValidationError(exc.messages) from exc

        cleaned_data['_active_traits'] = traits

        return cleaned_data



    def save(self, commit=True):

        instance = super().save(commit=commit)

        if not commit:

            return instance

        traits = self.cleaned_data.get('_active_traits', self._active_traits_from_form())

        set_active_traits_for_morphospecies(instance, traits, validate=False)

        return instance





class MorphospeciesCombineForm(Form):



    combine_to_id = IntegerField(

        required=False)

