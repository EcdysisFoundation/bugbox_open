from django.http import HttpResponseRedirect
from django.urls import reverse

from ..users.models import Eula


class EULAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path != reverse('core:eula') \
                and not request.path.startswith('/accounts'):
            if Eula.objects.first():
                if not request.user.agreed_to_eula:
                    return HttpResponseRedirect(reverse('core:eula'))

        response = self.get_response(request)
        return response
