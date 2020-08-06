from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField

from .base_model import BaseModel


class Question(BaseModel):
    text = models.CharField(max_length=256)
    answer = MarkdownxField()

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ('text',)

    def __str__(self):
        return self.text
