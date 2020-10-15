from django.db import models
from wagtail.core.query import PageQuerySet
from wagtail_recycle_bin.models import RecycleBinPage


class RecyclePageQuerySet(PageQuerySet):
    def exclude_recycle_bins(self):
        bins = RecycleBinPage.objects.all()

        if not bins.exists():
            return self

        bin_paths = bins.values_list("path", flat=True)

        q = models.Q()

        for path in bin_paths:
            q |= models.Q(path__startswith=path)

        return self.exclude(q)


class BaseRecycleManager(models.Manager):
    def get_queryset(self):
        return (super().get_queryset()).exclude_recycle_bins()


RecycleManager = BaseRecycleManager.from_queryset(RecyclePageQuerySet)
