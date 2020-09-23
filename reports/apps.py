from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _
from reports.signals import create_notice_types


class ReportsConfig(AppConfig):
    name = 'reports'
    verbose_name = _('Reports App')

    def ready(self):
        post_migrate.connect(create_notice_types, sender=self)
