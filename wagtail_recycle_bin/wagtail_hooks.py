from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import IndexView
from wagtail.contrib.modeladmin.helpers import ButtonHelper, PermissionHelper

from .utils import recycle_bin_for_request
from .models import RecycleBinPage, RecycleBin
from .views import recycle_delete, recycle_restore, recycle_move


class RecyclePermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False


class RecycleButtonHelper(ButtonHelper):
    restore_button_classnames = [
        "button-small",
        "button-secondary",
        "icon",
        "icon-undo",
    ]

    def restore_and_move_button(self, obj):
        return {
            "url": reverse("wagtail_recycle_bin_move", args=(obj.page.id,)),
            "label": "Restore and move",
            "classname": self.finalise_classname(self.restore_button_classnames),
            "title": "Restore and move",
        }

    def restore_button(self, obj):
        return {
            "url": reverse("wagtail_recycle_bin_restore", args=(obj.page.id,)),
            "label": "Restore",
            "classname": self.finalise_classname(self.restore_button_classnames),
            "title": "Restore",
        }

    def has_ancestor_in_bin(self, obj):
        parent = obj.get_parent()

        if not parent:
            return False

        ancestor_app_labels = list(
            parent.get_ancestors(inclusive=True).values_list(
                "content_type__app_label", flat=True
            )
        )

        return "wagtail_recycle_bin" in ancestor_app_labels

    def get_buttons_for_obj(
        self, obj, exclude=["edit"], classnames_add=None, classnames_exclude=None
    ):
        buttons = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude
        )

        if "restore" not in (exclude or []):
            parent = obj.parent
            if parent and not self.has_ancestor_in_bin(parent):
                buttons.append(self.restore_button(obj))
            buttons.append(self.restore_and_move_button(obj))

        return buttons


class RecycleBinModelAdmin(ModelAdmin):
    model = RecycleBin
    menu_label = "Recycle Bin"
    menu_icon = "bin"
    admin_order_field = "title"

    list_display = ("page_tree", "time_recycled", "user")
    # search_fields = ("title",)

    button_helper_class = RecycleButtonHelper
    permission_helper_class = RecyclePermissionHelper

    def page_tree(self, rb):
        descendants = rb.page.get_descendants(inclusive=True)

        depth = rb.page.depth
        output = ""

        for i, x in enumerate(descendants):
            output += "&nbsp;" * (x.depth - depth)

            if i == 0:
                output += "<strong>" + x.title + "</strong><br>"
            else:
                output += x.title + "<br>"

        return mark_safe(output)

    def get_queryset(self, request):
        # Create a bin if there is none
        recycle_bin_for_request(request)

        return super().get_queryset(request).prefetch_related("page")


modeladmin_register(RecycleBinModelAdmin)


@hooks.register("before_delete_page")
def delete_page(request, page):
    return recycle_delete(request, page)


@hooks.register("construct_page_chooser_queryset")
def exclude_recycle_bin_from_chooser(pages, request):
    pages = pages.not_type(RecycleBinPage)

    return pages


@hooks.register("construct_explorer_page_queryset")
def exclude_recycle_bin_from_explorer(parent_page, pages, request):
    pages = pages.not_type(RecycleBinPage)

    return pages


@hooks.register("register_admin_urls")
def urlconf_time():
    return [
        path(
            "wagtail_recycle_bin/restore_and_move/<int:page_id>/",
            recycle_move,
            name="wagtail_recycle_bin_move",
        ),
        path(
            "wagtail_recycle_bin/restore/<int:page_id>/",
            recycle_restore,
            name="wagtail_recycle_bin_restore",
        ),
    ]
