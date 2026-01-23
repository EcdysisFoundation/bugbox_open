from django.conf import settings


def grower_portal_constants(request):

    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }
