from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (DetailView, FormView, RedirectView,
                                  TemplateView, UpdateView)

from .forms import EulaForm
from .models import Eula

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class EulaView(LoginRequiredMixin, FormView):
    """
    View for the eula agreement
    """
    template_name = 'core/eula.html'
    form_class = EulaForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eula = Eula.objects.order_by('-timestamp').first()
        context.update({
            'eula_text': eula.eula_text if eula else 'EULA Placeholder',
            'effective_date': eula.timestamp if eula else ''
        })
        return context

    def get_success_url(self):
        """
        Redirect growers to profile completion or dashboard after EULA acceptance.
        """
        user = self.request.user
        
        # Check if user is a member of is_grower group
        if user.groups.filter(name='is_grower').exists():
            try:
                grower_profile = user.grower_profile
                if grower_profile.profile_completed:
                    return reverse('grower_portal:dashboard')
                else:
                    return reverse('grower_portal:profile_complete')
            except:
                # If no grower profile exists, redirect to profile completion
                return reverse('grower_portal:profile_complete')
        
        # For regular users, use default redirect
        return self.success_url

    def form_valid(self, form):
        """
        Overwrite user agreed to eula to be true
        """
        self.request.user.agreed_to_eula = True
        self.request.user.save()
        return HttpResponseRedirect(self.get_success_url())


class EulaReadView(TemplateView):
    """
    View of the EULA without a form.
    """
    template_name = 'core/eula_read.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eula = Eula.objects.order_by('-timestamp').first()
        context.update({
            'eula_text': eula.eula_text if eula else 'EULA Placeholder',
            'effective_date': eula.timestamp if eula else ''
        })
        return context
