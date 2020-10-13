from wagtail.core.models import Site, Page
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import IndexView

from .models import RecycleBinPage

class RecycleBinIndexView(IndexView):
    def get_ordering(self, request, queryset):
        return []


class RecycleBinModelAdmin(ModelAdmin):
    model = RecycleBinPage
    menu_label = "Recycle Bin"
    menu_icon = "bin"
    admin_order_field = "title"
    index_view_class = RecycleBinIndexView


    list_display = ("title", "live")
    search_fields = ("title",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        site = Site.find_for_request(request)

        recycle_bin = RecycleBinPage.objects.in_site(site)

        if not recycle_bin.exists():
            recycle_bin = RecycleBinPage(
                title="Recycle bin",
            )
            site.root_page.add_child(instance=recycle_bin)
            recycle_bin.save_revision()
        else:
            recycle_bin = recycle_bin.first()

        return recycle_bin.get_children()

modeladmin_register(RecycleBinModelAdmin)
