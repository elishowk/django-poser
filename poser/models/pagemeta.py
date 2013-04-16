from django.db import models
from django.utils.translation import ugettext_lazy as _
from .pagemodel import Page


class PageMeta(models.Model):
    """
    Untyped generic model metadata
    """
    page = models.ForeignKey(Page)
    key = models.CharField(_('key'),
                           max_length=255,
                           db_index=True
                           )
    value = models.TextField(_('value'))

    class Meta:
        app_label = "poser"
