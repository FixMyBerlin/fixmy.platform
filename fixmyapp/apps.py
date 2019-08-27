from django.apps import AppConfig
from djoser.signals import user_registered
from .signals import sign_up_newsletter_on_registration


class FixmyappConfig(AppConfig):
    name = 'fixmyapp'

    def ready(self):
        user_registered.connect(sign_up_newsletter_on_registration)
