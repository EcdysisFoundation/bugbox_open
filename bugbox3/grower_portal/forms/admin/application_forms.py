from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Row, Column, HTML, Div, Submit, Layout
from ..grower.forms import (
    ApplicationCreationForm
)

User = get_user_model()


class GrowerSelectionForm(forms.Form):
    """Initial form to select grower - can be existing account or new grower info"""
    
    grower_email = forms.EmailField(
        required=False,
        label='Grower Email (if account exists)',
        help_text='Email of existing grower account, or leave blank to enter grower info manually',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'grower@example.com (optional)'})
    )
    
    grower_name = forms.CharField(
        required=False,
        max_length=200,
        label='Grower Name',
        help_text='Full name of the grower (required if no email provided)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'})
    )
    
    grower_phone = forms.CharField(
        required=False,
        max_length=20,
        label='Grower Phone (Optional)',
        help_text='Contact phone number',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(555) 123-4567'})
    )
    
    grower_email_manual = forms.EmailField(
        required=False,
        label='Grower Email (for contact)',
        help_text='Email for contact purposes (not linked to account)',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@email.com (optional)'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        grower_email = cleaned_data.get('grower_email')
        grower_name = cleaned_data.get('grower_name')
        
        if not grower_email and not grower_name:
            raise ValidationError(
                'Please either enter an existing grower email OR provide the grower name for manual entry.'
            )
        
        if grower_email:
            try:
                user = User.objects.get(email=grower_email)
                if not user.groups.filter(name='is_grower').exists():
                    raise ValidationError({'grower_email': 'User exists but is not a grower'})
                cleaned_data['grower_user'] = user
            except User.DoesNotExist:
                raise ValidationError({
                    'grower_email': 'No grower found with this email. Leave blank and use manual entry instead.'
                })
        
        return cleaned_data


class AdminApplicationCreationForm(ApplicationCreationForm):
    """Step 1: Basic info, field type, date sampled - Admin version"""
    
    grower_email = forms.CharField(
        label='Grower Email',
        help_text='Email address of the grower (read-only).',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'placeholder': 'No email'}),
        required=False
    )
    
    def clean_grower_email(self):
        """Allow empty or 'No email' values, otherwise validate as email"""
        email = self.cleaned_data.get('grower_email', '').strip()
        if not email or email == 'No email':
            return ''
        try:
            validate_email(email)
            return email
        except ValidationError:
            raise forms.ValidationError('Enter a valid email address.')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'grower_email' in self.initial:
            if not self.initial.get('grower_email') or self.initial.get('grower_email') == '':
                self.initial['grower_email'] = 'No email'
        
        self.helper.form_action = '.'
        self.helper.disable_csrf = False
        self.helper.include_media = False
        self.use_required_attribute = False
    
    def get_primary_layout(self):
        base_layout = super().get_primary_layout()
        base_layout_without_submit = [item for item in base_layout if not isinstance(item, Submit)]
        return [
            Fieldset(
                'Grower Information',
                Row(Column('grower_email'))
            ),
            *base_layout_without_submit,
            Submit('submit', 'Next: Management Practices', css_class='btn btn-primary btn-lg')
        ]


class LinkGrowerForm(forms.Form):
    grower_email = forms.EmailField(
        required=False,
        label='Grower Email',
        help_text='Enter the email address of the grower account to link',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'grower@example.com'})
    )
    
    grower_search = forms.CharField(
        required=False,
        max_length=200,
        label='Search Grower',
        help_text='Search by name or email',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or email...'})
    )
    
    selected_grower_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            Fieldset(
                'Link to Grower Account',
                HTML('<p class="text-muted">You can either enter a grower email directly or search for a grower.</p>'),
                Row(Column('grower_email', css_class='col-md-12')),
                HTML('<p class="text-center my-2"><strong>OR</strong></p>'),
                Row(Column('grower_search', css_class='col-md-12')),
                'selected_grower_id',
                Div(
                    Submit('search', 'Search Growers', css_class='btn btn-secondary me-2'),
                    Submit('link', 'Link to Selected Grower', css_class='btn btn-primary'),
                    css_class='mt-3'
                )
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
    def clean_grower_email(self):
        email = self.cleaned_data.get('grower_email')
        if email:
            try:
                user = User.objects.get(email=email)
                if not user.groups.filter(name='is_grower').exists():
                    raise ValidationError('User exists but is not a grower. Please ensure the user has grower permissions.')
                return email
            except User.DoesNotExist:
                raise ValidationError('No grower found with this email address.')
        return email
    
    def clean_selected_grower_id(self):
        grower_id = self.cleaned_data.get('selected_grower_id')
        if grower_id:
            try:
                user = User.objects.get(id=grower_id)
                if not user.groups.filter(name='is_grower').exists():
                    raise ValidationError('Selected user is not a grower.')
                return grower_id
            except User.DoesNotExist:
                raise ValidationError('Selected grower does not exist.')
        return grower_id

