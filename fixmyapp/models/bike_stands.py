from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .report import Report

# This model is deprecated and retained in this place only for usage
# by migrations that transfer data from this model into the replacement
# in the `reports` django app.


class BikeStands(Report):
    number = models.PositiveSmallIntegerField(_('number'))
    fee_acceptable = models.BooleanField(_('fee_acceptable'), default=False)

    class Meta:
        verbose_name = _('bike stands')
        verbose_name_plural = _('bike stands')
