from wagtail.core.models import Page


class RecycleBinPage(Page):
    parent_page_types = []
    subpage_types = []
