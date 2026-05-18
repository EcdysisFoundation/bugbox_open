from django import forms
from django.core.exceptions import ValidationError

from ...constants import CLUSTER_NUMBER_MAX_LENGTH, LABEL_PROJECT_CHOICES
from ...models import LabelGeneration


class SubmittalFormGenerationForm(forms.Form):
    """Generate submittal forms for a chosen project, label batch, and sample codes."""

    project_type = forms.ChoiceField(
        choices=LABEL_PROJECT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_submittal_project_type',
        }),
        label='Project Type',
    )

    cluster_number = forms.CharField(
        max_length=CLUSTER_NUMBER_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., C1, C2',
            'id': 'id_cluster_number',
        }),
        label='Cluster Number',
        help_text='Enter the cluster number (e.g., C1, C2)',
    )

    year = forms.IntegerField(
        min_value=2020,
        max_value=2100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2024',
            'id': 'id_year',
        }),
        label='Year',
        help_text='Year for the submittal form',
    )

    label_generation_id = forms.ChoiceField(
        required=True,
        choices=[('', '-- Select cluster, year, and project first --')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_label_generation_id',
        }),
        label='Inner Label Generation',
        help_text='Choose which label batch to use (same cluster/year can exist for Avalanche and Ignite).',
    )

    selected_codes = forms.MultipleChoiceField(
        required=True,
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input submittal-code-checkbox'}),
        label='Sample / Transect Codes',
        help_text='Select which codes to include on the submittal form(s).',
    )

    generate_soil = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_generate_soil',
        }),
        label='Generate Soil Submittal Form',
        help_text='Generate submittal form for soil samples',
    )

    generate_plant = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_generate_plant',
        }),
        label='Generate Plant Submittal Form',
        help_text='Generate submittal form for plant samples (forage)',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bind_label_generation_choices()

    def _bind_label_generation_choices(self):
        """Populate generation and code choices on POST (validation / re-render after error)."""
        if not self.data:
            return
        project_type = (self.data.get('project_type') or '').strip()
        cluster = (self.data.get('cluster_number') or '').strip()
        year_raw = (self.data.get('year') or '').strip()
        if not project_type or not cluster or not year_raw:
            return
        try:
            year = int(year_raw)
        except ValueError:
            return

        generations = LabelGeneration.objects.filter(
            project_type=project_type,
            cluster_number=cluster,
            year=year,
            label_category='inner',
            status='ready',
        ).order_by('-generated_at')

        gen_choices = [('', '-- Select a label generation --')]
        for gen in generations:
            if (gen.generation_params or {}).get('ignite_forage_supplement'):
                continue
            n = len(gen.transect_codes_generated or [])
            gen_choices.append((
                str(gen.id),
                f'#{gen.id} — {gen.generated_at.strftime("%Y-%m-%d %H:%M")} — {n} code(s)',
            ))
        self.fields['label_generation_id'].choices = gen_choices

        gen_id = self.data.get('label_generation_id')
        if gen_id:
            try:
                gen = LabelGeneration.objects.get(pk=int(gen_id))
                codes = [str(c).strip() for c in (gen.transect_codes_generated or []) if str(c).strip()]
                self.fields['selected_codes'].choices = [(c, c) for c in codes]
            except (LabelGeneration.DoesNotExist, ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        project_type = cleaned_data.get('project_type')
        cluster = cleaned_data.get('cluster_number')
        year = cleaned_data.get('year')
        gen_id = cleaned_data.get('label_generation_id')
        selected = cleaned_data.get('selected_codes') or []

        if not cleaned_data.get('generate_soil') and not cleaned_data.get('generate_plant'):
            raise ValidationError('Select at least one submittal form type (Soil and/or Plant).')

        if not gen_id:
            raise ValidationError('Select an inner label generation for this cluster, year, and project.')

        try:
            label_gen = LabelGeneration.objects.get(pk=int(gen_id))
        except (LabelGeneration.DoesNotExist, ValueError, TypeError):
            raise ValidationError('The selected label generation was not found.')

        if label_gen.project_type != project_type:
            raise ValidationError('Label generation does not match the selected project type.')
        if label_gen.cluster_number != cluster or label_gen.year != year:
            raise ValidationError('Label generation does not match cluster number and year.')
        if label_gen.label_category != 'inner':
            raise ValidationError('Submittal forms require an inner label generation.')
        if label_gen.status != 'ready':
            raise ValidationError('The selected label generation is not ready yet.')

        available = {str(c).strip() for c in (label_gen.transect_codes_generated or []) if str(c).strip()}
        if not available:
            raise ValidationError('The selected label generation has no stored codes.')

        if not selected:
            raise ValidationError('Select at least one code to include on the submittal form(s).')

        invalid = set(selected) - available
        if invalid:
            raise ValidationError(
                'Some selected codes are not part of this label generation: '
                + ', '.join(sorted(invalid)[:10])
                + ('…' if len(invalid) > 10 else '')
            )

        cleaned_data['label_generation'] = label_gen
        ordered = [c for c in (label_gen.transect_codes_generated or []) if str(c).strip() in selected]
        cleaned_data['selected_codes_ordered'] = ordered
        return cleaned_data
