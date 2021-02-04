from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .section import Section


class SectionAccidents(BaseModel):
    """Accident data for a section."""

    section = models.ForeignKey(
        Section, related_name='accidents', on_delete=models.CASCADE
    )

    killed = models.IntegerField(_('killed'))
    severely_injured = models.IntegerField(_('severely injured'))
    slightly_injured = models.IntegerField(_('slightly injured'))
    source = models.TextField(_('source'), blank=True, null=True)

    RISK_LEVEL_CHOICES = (
        (3, _('accident blackspot')),
        (2, _('some accidents')),
        (1, _('one accident')),
        (0, _('no accidents')),
    )
    risk_level = models.PositiveSmallIntegerField(
        _('risk level'), choices=RISK_LEVEL_CHOICES
    )

    class Meta:
        verbose_name = _('Section accident data')
        verbose_name_plural = _('Section accident datasets')

    def __str__(self):
        return f"{_('Section accident data')} {str(self.section)}"
