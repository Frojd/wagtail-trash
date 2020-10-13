from django.urls import path
from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import IndexView

from .utils import recycle_bin_for_request
from .models import RecycleBinPage
from .views import recycle_delete


class RecycleBinModelAdmin(ModelAdmin):
    model = Page
    menu_label = "Recycle Bin"
    menu_icon = "bin"
    admin_order_field = "title"

    list_display = ("title", "sub_pages")
    search_fields = ("title",)

    def sub_pages(self, page):
        return [x.title for x in page.get_descendants()]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        recycle_bin = recycle_bin_for_request(request)

        return recycle_bin.get_children()


modeladmin_register(RecycleBinModelAdmin)


@hooks.register("before_delete_page")
def delete_page(request, page):
    return recycle_delete(request, page)
