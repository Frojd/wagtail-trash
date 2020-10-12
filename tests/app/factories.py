from wagtail_factories import PageFactory
from wagtail_recycle_bin.models import RecycleBinPage


class BasePageFactory(PageFactory):
    class Meta:
        model = RecycleBinPage
