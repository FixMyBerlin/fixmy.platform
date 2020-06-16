import pytz
from django.utils import timezone


class TimezoneMiddleware:
    """Render all timezone aware datetime objects as Berlin time"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone.activate(pytz.timezone('Europe/Berlin'))
        return self.get_response(request)
