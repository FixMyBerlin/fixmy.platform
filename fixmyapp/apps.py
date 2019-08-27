from django.apps import AppConfig
from django.conf import settings
from djoser.signals import user_registered
from .signals import sign_up_newsletter_on_registration


class FixmyappConfig(AppConfig):
    name = 'fixmyapp'

    def ready(self):
        if settings.TOGGLE_NEWSLETTER:
            user_registered.connect(sign_up_newsletter_on_registration)
