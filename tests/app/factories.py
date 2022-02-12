from wagtail_factories import PageFactory

from wagtail_trash.models import TrashCanPage


class BasePageFactory(PageFactory):
    class Meta:
        model = TrashCanPage
