from django.conf import settings
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


def create_notice_types(sender, **kwargs):
    if "pinax.notifications" in settings.INSTALLED_APPS:
        from pinax.notifications.models import NoticeType

        NoticeType.create(
            "reports_update",
            _("Report Status Updated"),
            _("your watched reports have been updated"),
        )
    else:
        # Skipping creation of NoticeTypes as notification app not found
        pass


class ReportsConfig(AppConfig):
    name = 'reports'
    verbose_name = _('Reports App')

    def ready(self):
        post_migrate.connect(create_notice_types, sender=self)
