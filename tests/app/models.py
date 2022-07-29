from wagtail.core.models import Page, PageManager

from wagtail_trash.managers import TrashManager


class TestPage(Page):
    objects = PageManager()
    objects_excluding_bins = TrashManager()


class OtherPage(Page):
    objects = PageManager()
    objects_excluding_bins = TrashManager()
