from crispy_forms.layout import HTML, Column, Field, Layout, Row

from django.core.exceptions import ValidationError

from django.forms import (

    BooleanField,

    CharField,

    ChoiceField,

    DecimalField,

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
    FUNCTIONAL_GROUP_WEIGHT_GUIDE,
    LIFE_STAGE_FORM_HELP,
    OTHER_SECTION_HELP,
    PARENT_SUBTYPE_SECTION_HELP,
)

from .functional_group_validation import (
    infer_missing_parent_weights,
    parse_weight_field,
    validate_functional_group_weights,
)

from .functional_groups import get_trait_weights_for_morphospecies, set_trait_weights_for_morphospecies

from .models import FunctionalGroup, Morphospecies



FG_WEIGHT_FIELD_PREFIX = 'fg_weight_'





def functional_group_weight_field_name(code: str) -> str:

    return f'{FG_WEIGHT_FIELD_PREFIX}{code}'





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



        existing_weights = {}

        if self.instance and self.instance.pk:

            existing_weights = get_trait_weights_for_morphospecies(self.instance)

            if existing_weights.get('young_terrestrial'):

                self.fields['young_habitat'].initial = 'young_terrestrial'

            elif existing_weights.get('young_aquatic'):

                self.fields['young_habitat'].initial = 'young_aquatic'

            if existing_weights.get('adult_terrestrial'):

                self.fields['adult_habitat'].initial = 'adult_terrestrial'

            elif existing_weights.get('adult_aquatic'):

                self.fields['adult_habitat'].initial = 'adult_aquatic'



        for section in FUNCTIONAL_GROUP_UI_SECTIONS:

            if section['key'] == 'life_stage':

                continue

            codes = []

            if section['parent_code']:

                codes.append(section['parent_code'])

            codes.extend(section['subtype_codes'])

            for code in codes:

                field_name = functional_group_weight_field_name(code)

                fg = self._functional_groups_by_code.get(code)

                label = fg.display_name if fg else code

                self.fields[field_name] = DecimalField(

                    min_value=0,

                    max_value=1,

                    max_digits=4,

                    decimal_places=3,

                    required=False,

                    label=label,

                )

                if code in existing_weights:

                    self.fields[field_name].initial = existing_weights[code]

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

            HTML(self._build_functional_groups_guide_html()),

            HTML('<h6 class="mb-2">Life stage</h6>'),

            HTML(f'<p class="text-muted small mb-2">{escape(LIFE_STAGE_FORM_HELP)}</p>'),

            Row(

                Column('young_habitat'),

                Column('adult_habitat'),

            ),

            self._build_functional_groups_html(),

        ]



    def _build_functional_groups_guide_html(self) -> str:
        sections = []
        for title, paragraphs in FUNCTIONAL_GROUP_WEIGHT_GUIDE:
            body = ''.join(
                f'<p class="mb-2">{paragraph}</p>' for paragraph in paragraphs
            )
            sections.append(
                f'<div class="mb-3">'
                f'<div class="fw-semibold mb-1">{title}</div>'
                f'{body}'
                f'</div>'
            )
        return (
            f'<p class="text-muted small mb-2">{escape(FUNCTIONAL_GROUP_FORM_INTRO)}</p>'
            '<div class="accordion mb-3" id="fg-form-guide">'
            '<div class="accordion-item">'
            '<h2 class="accordion-header">'
            '<button class="accordion-button collapsed py-2" type="button" '
            'data-bs-toggle="collapse" data-bs-target="#fg-form-guide-body" '
            'aria-expanded="false" aria-controls="fg-form-guide-body">'
            'What do weights mean?'
            '</button></h2>'
            '<div id="fg-form-guide-body" class="accordion-collapse collapse" '
            'data-bs-parent="#fg-form-guide">'
            f'<div class="accordion-body small">{"".join(sections)}</div>'
            '</div></div></div>'
        )

    def _fg_weight_input_html(
        self,
        *,
        field_name: str,
        code: str,
        value,
        parent_code: str | None,
        extra_class: str = '',
    ) -> str:
        fg = self._functional_groups_by_code.get(code)
        description = escape(fg.description) if fg else ''
        label = escape(fg.display_name if fg else code)
        value_str = escape(str(value) if value not in (None, '') else '')
        parent_attr = escape(parent_code or '')
        return (
            f'<div class="col-md-4 col-lg-3 fg-trait-field" data-fg-code="{escape(code)}">'
            f'<label class="form-label" for="id_{field_name}">{label}</label>'
            f'<input type="number" step="0.001" min="0" max="1" '
            f'class="form-control fg-weight-input {extra_class}" name="{field_name}" '
            f'id="id_{field_name}" value="{value_str}" '
            f'data-fg-parent="{parent_attr}" data-fg-code="{escape(code)}">'
            f'<div class="form-text fg-trait-description">{description}</div>'
            f'</div>'
        )

    def _build_parent_subtype_section_html(self, section: dict) -> str:
        parent_code = section['parent_code']
        subtype_codes = section['subtype_codes']
        section_key = section['key']
        title = escape(section['title'])
        help_text = escape(PARENT_SUBTYPE_SECTION_HELP.get(section_key, ''))
        parent_field = functional_group_weight_field_name(parent_code)
        parent_fg = self._functional_groups_by_code.get(parent_code)
        parent_label = escape(parent_fg.display_name if parent_fg else parent_code)
        parent_value = self[parent_field].value() if parent_field in self.fields else ''
        if parent_value is None:
            parent_value = ''

        picker_options = ['<option value="">Select one feeding type</option>']
        for code in subtype_codes:
            fg = self._functional_groups_by_code.get(code)
            picker_options.append(
                f'<option value="{escape(code)}">{escape(fg.display_name if fg else code)}</option>'
            )

        parts = [
            f'<div class="card mb-3 fg-section fg-section-parent" '
            f'data-fg-section="{escape(section_key)}" data-parent-code="{escape(parent_code)}">',
            '<div class="card-header d-flex justify-content-between align-items-center py-2">',
            f'<span class="fw-semibold">{title}</span>',
            '<span class="fg-section-status badge bg-secondary">Not set</span>',
            '</div>',
            '<div class="card-body">',
            f'<p class="small text-muted mb-3">{help_text}</p>',
            '<div class="row align-items-end g-2 mb-3 fg-parent-block">',
            '<div class="col-md-4 col-lg-3">',
            f'<label class="form-label" for="id_{parent_field}">{parent_label} (overall)</label>',
            f'<input type="number" step="0.001" min="0" max="1" '
            f'class="form-control fg-weight-input fg-parent-weight" name="{parent_field}" '
            f'id="id_{parent_field}" value="{escape(str(parent_value) if parent_value != "" else "")}" '
            f'data-fg-parent="{escape(parent_code)}" data-fg-code="{escape(parent_code)}">',
            '</div>',
            '<div class="col-md-8 col-lg-9">',
            '<div class="btn-group btn-group-sm flex-wrap" role="group">',
            '<button type="button" class="btn btn-outline-secondary fg-preset" data-value="0.5">½ mixed</button>',
            '<button type="button" class="btn btn-outline-secondary fg-preset" data-value="1">1 pure</button>',
            '<button type="button" class="btn btn-outline-secondary fg-clear-section">Clear section</button>',
            '</div>',
            '</div>',
            '</div>',
            '<div class="mb-3 fg-quick-single">',
            '<label class="form-label small">Single feeding type (sets parent to 1)</label>',
            f'<select class="form-select form-select-sm fg-single-subtype-picker" '
            f'data-parent-code="{escape(parent_code)}">',
            ''.join(picker_options),
            '</select>',
            '</div>',
            '<div class="fg-subtypes-block">',
            '<div class="d-flex justify-content-between align-items-center mb-1">',
            '<label class="form-label small mb-0">Subtype detail</label>',
            '<span class="fg-subtype-sum-label small text-muted"></span>',
            '</div>',
            '<div class="progress mb-2 fg-subtype-sum" style="height: 8px;">',
            '<div class="progress-bar" role="progressbar" style="width: 0%"></div>',
            '</div>',
            '<div class="row g-2 fg-subtype-grid">',
        ]

        for code in subtype_codes:
            field_name = functional_group_weight_field_name(code)
            if field_name not in self.fields:
                continue
            value = self[field_name].value()
            if value is None:
                value = ''
            parts.append(
                self._fg_weight_input_html(
                    field_name=field_name,
                    code=code,
                    value=value,
                    parent_code=parent_code,
                    extra_class='fg-subtype-weight',
                )
            )

        parts.extend([
            '</div>',
            '<div class="fg-subtype-hint small mt-1"></div>',
            '</div>',
            '</div>',
            '</div>',
        ])
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
            '<div class="row g-2">',
        ]
        for code in section['subtype_codes']:
            field_name = functional_group_weight_field_name(code)
            if field_name not in self.fields:
                continue
            fg = self._functional_groups_by_code.get(code)
            value = self[field_name].value()
            if value is None:
                value = ''
            is_checked = bool(value and float(value) > 0)
            checked = ' checked' if is_checked else ''
            value_str = escape(str(value) if value not in (None, '') else '')
            label = escape(fg.display_name if fg else code)
            description = escape(fg.description) if fg else ''
            parts.append(
                f'<div class="col-md-6 col-lg-4">'
                f'<div class="form-check fg-other-check">'
                f'<input type="checkbox" class="form-check-input fg-other-toggle" '
                f'id="toggle_{field_name}" data-target="{field_name}"{checked}>'
                f'<label class="form-check-label" for="toggle_{field_name}">{label}</label>'
                f'<div class="form-text">{description}</div>'
                f'</div>'
                f'<input type="number" step="0.001" min="0" max="1" '
                f'class="form-control fg-weight-input fg-other-weight d-none" name="{field_name}" '
                f'id="id_{field_name}" value="{value_str}" '
                f'data-fg-parent="" data-fg-code="{escape(code)}">'
                f'</div>'
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



    def _collect_trait_weights(self) -> dict[str, float]:

        weights: dict[str, float] = {}

        for name, value in self.cleaned_data.items():

            if not name.startswith(FG_WEIGHT_FIELD_PREFIX):

                continue

            code = name[len(FG_WEIGHT_FIELD_PREFIX):]

            weight = parse_weight_field(value)

            if weight > 0:

                weights[code] = weight



        young = self.cleaned_data.get('young_habitat')

        adult = self.cleaned_data.get('adult_habitat')

        if young:

            weights[young] = 1.0

        if adult:

            weights[adult] = 1.0

        return weights



    def clean(self):

        cleaned_data = super().clean()

        weights = {}

        errors = {}

        for name, value in cleaned_data.items():

            if not name.startswith(FG_WEIGHT_FIELD_PREFIX):

                continue

            try:

                weight = parse_weight_field(value)

            except ValidationError as exc:

                errors[name] = exc.messages

                continue

            code = name[len(FG_WEIGHT_FIELD_PREFIX):]

            if weight > 0:

                weights[code] = weight



        young = cleaned_data.get('young_habitat')

        adult = cleaned_data.get('adult_habitat')

        if young:

            weights[young] = 1.0

        if adult:

            weights[adult] = 1.0



        if errors:

            raise ValidationError(errors)

        weights = infer_missing_parent_weights(weights)

        try:

            validate_functional_group_weights(weights)

        except ValidationError as exc:

            raise ValidationError(exc.messages) from exc



        cleaned_data['_trait_weights'] = weights

        return cleaned_data



    def save(self, commit=True):

        instance = super().save(commit=commit)

        if not commit:

            return instance

        weights = self.cleaned_data.get('_trait_weights', self._collect_trait_weights())

        set_trait_weights_for_morphospecies(instance, weights, validate=False)

        return instance





class MorphospeciesCombineForm(Form):



    combine_to_id = IntegerField(

        required=False)


