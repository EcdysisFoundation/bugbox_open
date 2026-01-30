from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import AGE_MAX, AGE_MIN, GENDER_CHOICES, PHONE_MAX_LENGTH, RACE_CHOICES, STATUS_MAX_LENGTH

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
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text='State or province'
    )
    city = models.CharField(
        max_length=200,
        blank=True,
        help_text='City'
    )
    county = models.CharField(
        max_length=200,
        blank=True,
        help_text='County'
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text='Country'
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
