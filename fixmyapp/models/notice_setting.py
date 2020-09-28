import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class NoticeSetting(models.Model):
    """A user's preference to receive notifications of a certain type"""

    REPORT_UPDATE_KIND = 'report_update'

    NOTICE_KINDS = ((REPORT_UPDATE_KIND, _('report status update')),)

    access_key = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="notice_settings",
    )
    send = models.BooleanField(_("send"), default=True)
    kind = models.CharField(max_length=32, choices=NOTICE_KINDS)

    class Meta:
        verbose_name = _("notice setting")
        verbose_name_plural = _("notice settings")
        unique_together = ['user', 'kind']
