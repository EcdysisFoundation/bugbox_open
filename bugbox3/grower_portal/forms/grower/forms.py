from django import forms
from django.contrib.auth import get_user_model
from ...models import GrowerProfile

User = get_user_model()


class GrowerProfileCompletionForm(forms.ModelForm):
    """
    Form for completing grower profile information during initial signup.
    This form is shown only once after grower registration.
    """
    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    RACE_CHOICES = [
        ('', 'Select Race'),
        ('american_indian_alaska_native', 'American Indian or Alaska Native'),
        ('asian', 'Asian'),
        ('black_african_american', 'Black or African American'),
        ('native_hawaiian_pacific_islander', 'Native Hawaiian or Other Pacific Islander'),
        ('white', 'White'),
        ('two_or_more_races', 'Two or More Races'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Phone Number'
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        label='Gender'
    )
    age = forms.IntegerField(
        required=False,
        label='Age',
        help_text='Enter your age in years',
        min_value=1,
        max_value=120
    )
    race = forms.ChoiceField(
        choices=RACE_CHOICES,
        required=False,
        label='Race'
    )

    class Meta:
        model = GrowerProfile
        fields = ['phone', 'gender', 'age', 'race']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})