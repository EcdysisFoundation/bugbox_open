from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.forms import BooleanField, CharField, Form
from django.utils.translation import gettext_lazy as _
from bugbox3.core.permissions import IS_GROWER_USER

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """
    name = CharField(max_length=255, label='Name of User')
    is_grower = BooleanField(required=False, label='Sign up as Grower')
    
    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data["name"]
        user.save()
        
        # Add user to is_grower group if checkbox is checked
        if self.cleaned_data.get("is_grower"):
            grower_group, created = Group.objects.get_or_create(name='is_grower')
            
            if not grower_group.permissions.exists():
                permissions_to_add = []
                for perm_string in IS_GROWER_USER:
                    app_label, codename = perm_string.split('.')
                    try:
                        perm = Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=codename
                        )
                        permissions_to_add.append(perm)
                    except Permission.DoesNotExist:
                        pass
                
                if permissions_to_add:
                    grower_group.permissions.set(permissions_to_add)
            
            user.groups.add(grower_group)
        
        return user


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class EulaForm(Form):
    """
    form for user to agree to terms of service
    """
    agree_to_terms = BooleanField(required=False)

    def clean_agree_to_terms(self):
        if not self.cleaned_data['agree_to_terms']:
            raise ValidationError('You must agree to terms to proceed.')

        return self.cleaned_data['agree_to_terms']
