from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
    modified_date = models.DateTimeField(_('Modified date'), auto_now=True)

    class Meta:
        abstract = True
