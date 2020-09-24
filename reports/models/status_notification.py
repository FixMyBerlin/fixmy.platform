from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from pinax.notifications.models import NoticeType

from .report import Report


class StatusNotification(models.Model):
    """Represents a notification to a user about a status change"""

    date = models.DateField(_('date'), auto_now_add=True)
    kind = models.ForeignKey(
        NoticeType, on_delete=models.CASCADE, verbose_name=_('kind of notification')
    )
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, verbose_name=_('report')
    )
    sent = models.BooleanField(_('sent'), default=False)
    status = models.CharField(_('status'), max_length=20, choices=Report.STATUS_CHOICES)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, verbose_name=_('user')
    )
