from wagtail.core.models import Page
from wagtail_recycle_bin.managers import RecycleManager


class TestPage(Page):
    objects_excluding_bins = RecycleManager()


class OtherPage(Page):
    objects_excluding_bins = RecycleManager()
