from django.db import models
from cards.models import URLBatch


class URLBatchArchived(URLBatch):
    class Meta:
        proxy = True
        verbose_name = 'URL Archive'
        verbose_name_plural = 'URL Archive'
