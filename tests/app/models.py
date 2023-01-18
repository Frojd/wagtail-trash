from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail.models import Page, PageManager
else:
    from wagtail.core.models import Page, PageManager

from wagtail_trash.managers import TrashManager


class TestPage(Page):
    objects = PageManager()
    objects_excluding_bins = TrashManager()


class OtherPage(Page):
    objects = PageManager()
    objects_excluding_bins = TrashManager()
