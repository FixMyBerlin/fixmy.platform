from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel


class Photo(BaseModel):
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    copyright = models.CharField(_('copyright'), blank=True, null=True, max_length=256)
    object_id = models.PositiveIntegerField()
    src = models.ImageField(upload_to='photos', verbose_name=_('file'))

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')

    def __str__(self):
        return self.src.name.split('/')[-1]
