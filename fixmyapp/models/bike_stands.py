from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .report import Report


class BikeStands(Report):
    number = models.PositiveSmallIntegerField(_('number'))
    fee_acceptable = models.BooleanField(_('fee_acceptable'), default=False)

    class Meta:
        verbose_name = _('bike stands')
        verbose_name_plural = _('bike stands')
