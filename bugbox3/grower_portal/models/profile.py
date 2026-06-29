from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import (
    ADDRESS_LINE_MAX_LENGTH,
    AGE_MAX,
    AGE_MIN,
    GENDER_CHOICES,
    PHONE_MAX_LENGTH,
    POSTAL_CODE_MAX_LENGTH,
    RACE_ANOTHER_BACKGROUND,
    RACE_CHOICES,
    RACE_INDIGENOUS,
    RACE_INDIGENOUS_COUNTRY_MAX_LENGTH,
    RACE_OTHER_MAX_LENGTH,
    STATUS_MAX_LENGTH,
)
from ..country_choices import COUNTRY_CHOICES, COUNTRY_CODE_TO_NAME

User = get_user_model()


class GrowerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='grower_profile'
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        null=True
    )
    gender = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    age = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Age in years',
        validators=[MinValueValidator(AGE_MIN), MaxValueValidator(AGE_MAX)]
    )
    race = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=RACE_CHOICES,
        blank=True,
        null=True
    )
    race_indigenous_country = models.CharField(
        max_length=RACE_INDIGENOUS_COUNTRY_MAX_LENGTH,
        choices=COUNTRY_CHOICES,
        blank=True,
        help_text='Country associated with Indigenous / First Nations / Native selection',
    )
    race_other = models.CharField(
        max_length=RACE_OTHER_MAX_LENGTH,
        blank=True,
    )
    address_line = models.CharField(
        max_length=ADDRESS_LINE_MAX_LENGTH,
        blank=True,
        help_text='Street address',
    )
    address_line_2 = models.CharField(
        max_length=ADDRESS_LINE_MAX_LENGTH,
        blank=True,
        help_text='Apartment, unit or suite (optional)',
    )
    city = models.CharField(
        max_length=200,
        blank=True,
        help_text='City',
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text='State or province',
    )
    county = models.CharField(
        max_length=200,
        blank=True,
        help_text='County',
    )
    postal_code = models.CharField(
        max_length=POSTAL_CODE_MAX_LENGTH,
        blank=True,
        help_text='Postal or ZIP code',
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text='Country',
    )
    profile_completed = models.BooleanField(
        default=False,
        help_text='Whether the initial profile completion has been done'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Grower Profile')
        verbose_name_plural = _('Grower Profiles')
        permissions = [
            ('manage_grower_profiles', 'Can manage grower profiles'),
        ]

    def __str__(self):
        return f"{self.user.name} ({self.user.email})"

    def get_race_display_full(self):
        if not self.race:
            return ''

        label = self.get_race_display()
        if self.race == RACE_INDIGENOUS and self.race_indigenous_country:
            country_name = COUNTRY_CODE_TO_NAME.get(self.race_indigenous_country, self.race_indigenous_country)
            label = f'{label} ({country_name})'
        if self.race == RACE_ANOTHER_BACKGROUND and self.race_other:
            label = f'{label}: {self.race_other}'
        return label

    def get_country_display_name(self):
        if not self.country:
            return ''
        return COUNTRY_CODE_TO_NAME.get(self.country, self.country)

    def get_address_display(self):
        parts = []
        if self.address_line:
            parts.append(self.address_line)
        if self.address_line_2:
            parts.append(self.address_line_2)

        city_state = []
        if self.city:
            city_state.append(self.city)
        if self.state:
            city_state.append(self.state)
        if city_state:
            parts.append(', '.join(city_state))

        if self.county:
            parts.append(self.county)
        if self.postal_code:
            parts.append(self.postal_code)

        country_name = self.get_country_display_name()
        if country_name:
            parts.append(country_name)

        return ', '.join(parts)
