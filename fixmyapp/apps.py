from django.apps import AppConfig
from django.conf import settings
from djoser.signals import user_activated
from .signals import sign_up_newsletter_on_activation


class FixmyappConfig(AppConfig):
    name = 'fixmyapp'

    def ready(self):
        if settings.TOGGLE_NEWSLETTER:
            user_activated.connect(sign_up_newsletter_on_activation)
