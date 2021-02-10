from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel


class Section(BaseModel):
    street_name = models.CharField(_('street name'), max_length=255)
    suffix = models.CharField(_('suffix'), blank=True, null=True, max_length=3)
    borough = models.CharField(_('borough'), blank=True, null=True, max_length=255)
    street_category = models.PositiveSmallIntegerField(_('street category'), null=True)
    geometry = models.MultiLineStringField(_('geometry'), srid=4326, null=True)
    is_road = models.BooleanField(_('is road section'), default=True)

    class Meta:
        verbose_name = _('section')
        verbose_name_plural = _('sections')

    def velocity_index(self):
        if len(self.details.all()) > 0:
            return sum(d.velocity_index() for d in self.details.all()) / len(
                self.details.all()
            )
        else:
            return 0

    def safety_index(self):
        if len(self.details.all()) > 0:
            return sum(d.safety_index() for d in self.details.all()) / len(
                self.details.all()
            )
        else:
            return 0

    def __str__(self):
        section_type = _('road section') if self.is_road else _('intersection')
        return '{} {} ({})'.format(section_type, self.street_name, self.id)
