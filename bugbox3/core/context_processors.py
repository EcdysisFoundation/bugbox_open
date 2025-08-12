from django.conf import settings


def global_settings(request):
    """
    Provide context to global templates.
    """
    return {
        'ON_ECDYSIS_SERVER': True if settings.ON_ECDYSIS_SERVER == 'YES' else False
    }
