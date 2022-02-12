from wagtail.core.models import Page

from wagtail_trash.managers import TrashManager


class TestPage(Page):
    objects_excluding_bins = TrashManager()


class OtherPage(Page):
    objects_excluding_bins = TrashManager()
