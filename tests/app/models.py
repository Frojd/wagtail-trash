from wagtail.models import Page, PageManager

from wagtail_trash.managers import TrashManager
from wagtail_trash.mixins import SkipSitemapIfInTrashMixin


class TestPage(SkipSitemapIfInTrashMixin, Page):
    objects = PageManager()
    objects_excluding_bins = TrashManager()


class OtherPage(SkipSitemapIfInTrashMixin, Page):
    objects = PageManager()
    objects_excluding_bins = TrashManager()


class SectionPage(Page):
    pass


class ArticlePage(Page):
    parent_page_types = ["app.SectionPage"]


class SingletonPage(Page):
    max_count_per_parent = 1
