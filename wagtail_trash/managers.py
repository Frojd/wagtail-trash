from django.db import models
from wagtail.core.query import PageQuerySet
from wagtail_trash.models import TrashCanPage


class TrashCanPageQuerySet(PageQuerySet):
    def exclude_trash(self):
        bins = TrashCanPage.objects.all()

        if not bins.exists():
            return self

        bin_paths = bins.values_list("path", flat=True)

        q = models.Q()

        for path in bin_paths:
            q |= models.Q(path__startswith=path)

        return self.exclude(q)


class BaseTrashManager(models.Manager):
    def get_queryset(self):
        return (super().get_queryset()).exclude_trash()


TrashManager = BaseTrashManager.from_queryset(TrashCanPageQuerySet)
