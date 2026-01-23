from datetime import datetime

import pytz
from django.utils import timezone


class TimezoneDetectionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and 'timezone' in request.POST:
            user_timezone = request.POST.get('timezone')
            if user_timezone and self._is_valid_timezone(user_timezone):
                request.session['user_timezone'] = user_timezone

        request.user_timezone = self._get_user_timezone(request)

        response = self.get_response(request)
        return response

    def _get_user_timezone(self, request):
        return request.session.get('user_timezone', 'UTC')

    def _is_valid_timezone(self, tz_string):
        try:
            pytz.timezone(tz_string)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False


def get_user_timezone(request):
    return getattr(request, 'user_timezone', 'UTC')


def convert_to_user_timezone(dt, user_tz_string):
    if not dt:
        return dt

    if hasattr(dt, 'date') and not hasattr(dt, 'tzinfo'):
        dt = timezone.make_aware(datetime.combine(dt, datetime.min.time()), timezone.utc)
    elif not dt.tzinfo:
        dt = timezone.make_aware(dt, timezone.utc)

    try:
        user_tz = pytz.timezone(user_tz_string)
        return dt.astimezone(user_tz)
    except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
        return dt.astimezone(timezone.utc)
