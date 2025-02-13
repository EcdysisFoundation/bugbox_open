from django.contrib.auth.models import AbstractUser
from django.db.models import (BooleanField, CharField, DateTimeField, Model,
                              PositiveSmallIntegerField, TextField)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for bugbox3.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    role = PositiveSmallIntegerField(blank=True, default=1)
    agreed_to_eula = BooleanField(default=False, blank=True)

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


class Eula(Model):
    """
    Model for end user license agreement.
    """
    timestamp = DateTimeField(auto_now=True, editable=False)
    eula_text = TextField()

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        """
        Clears agreed_to_eula.
        """
        super().save(*args, **kwargs)
        User.objects.filter(agreed_to_eula=True).update(agreed_to_eula=False)

    def __str__(self):
        """
        String representation of the model
        """
        return 'Eula for {}'.format(self.timestamp)
