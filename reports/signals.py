from django.conf import settings
from django.utils.translation import gettext as _


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
