from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PermitsConfig(AppConfig):
    name = 'permits'
    verbose_name = _('Permits App')
