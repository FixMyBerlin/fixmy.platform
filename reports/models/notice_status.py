from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from fixmyapp.models import NoticeSetting
from .report import Report


class StatusNotice(models.Model):
    """Represents a notification to a user about a status change"""

    date = models.DateField(_('date'), auto_now_add=True)
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, verbose_name=_('report')
    )
    sent = models.BooleanField(_('sent'), default=False)
    status = models.CharField(_('status'), max_length=20, choices=Report.STATUS_CHOICES)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, verbose_name=_('user')
    )

    class Meta:
        verbose_name = _("status notice")
        verbose_name_plural = _("status notices")

    @classmethod
    def create(cls, *args, **kwargs):
        setting, _created = NoticeSetting.objects.get_or_create(
            user=kwargs.get("user"), kind=NoticeSetting.REPORT_UPDATE_KIND
        )
        if setting.send:
            return cls(*args, **kwargs).save()
