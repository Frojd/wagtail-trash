from django.shortcuts import reverse
from django.urls import path
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from wagtail import hooks
from wagtail.admin.views.pages.bulk_actions.delete import DeleteBulkAction
from wagtail_modeladmin.helpers import ButtonHelper, PermissionHelper
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail_modeladmin.views import DeleteView, IndexView

from .models import TrashCan, TrashCanPage
from .utils import is_in_trash, trash_can_for_request
from .views import trash_bulk_delete, trash_delete, trash_move, trash_restore


class TrashPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False


class TrashButtonHelper(ButtonHelper):
    restore_button_classnames = [
        "button-small",
        "button-secondary",
        "icon",
        "icon-undo",
    ]

    def restore_and_move_button(self, obj):
        return {
            "url": reverse("wagtail_trash_move", args=(obj.page.id,)),
            "label": _("Restore and move"),
            "classname": self.finalise_classname(self.restore_button_classnames),
            "title": _("Restore and move"),
        }

    def restore_button(self, obj):
        return {
            "url": reverse("wagtail_trash_restore", args=(obj.page.id,)),
            "label": _("Restore"),
            "classname": self.finalise_classname(self.restore_button_classnames),
            "title": _("Restore"),
        }

    def get_buttons_for_obj(
        self, obj, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        if exclude is None:
            exclude = ["edit"]
        buttons = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude
        )

        if "restore" not in (exclude or []):
            parent = obj.parent
            if parent and not is_in_trash(parent):
                buttons.append(self.restore_button(obj))
            buttons.append(self.restore_and_move_button(obj))

        return buttons


class TrashCanIndexView(IndexView):
    def get_page_title(self):
        return _("Trash Can")


class TrashCanDeleteView(DeleteView):
    def confirmation_message(self):
        return _(
            "Are you sure you want to delete this %(object)s? If other things in your "
            "site are related to it, they may also be affected."
        ) % {"object": _("page")}

    def delete_instance(self):
        rb = self.instance
        page = rb.page

        page.delete(user=self.request.user)
        rb.delete()


class TrashCanModelAdmin(ModelAdmin):
    model = TrashCan
    menu_label = _("Trash Can")
    menu_icon = "bin"
    admin_order_field = "title"

    list_display = ("page_tree", "time_recycled", "user")

    button_helper_class = TrashButtonHelper
    permission_helper_class = TrashPermissionHelper

    index_view_class = TrashCanIndexView
    index_template_name = "wagtail_trash/index.html"

    delete_view_class = TrashCanDeleteView

    def page_tree(self, rb):
        descendants = rb.page.get_descendants(inclusive=True)

        depth = rb.page.depth
        rows = []

        for i, x in enumerate(descendants):
            indent = mark_safe("&nbsp;" * (x.depth - depth))  # noqa: S308
            title = format_html("<strong>{}</strong>", x.title) if i == 0 else x.title
            rows.append((indent, title))

        return format_html_join("", "{}{}<br>", rows)

    def get_queryset(self, request):
        # Create a bin if there is none
        trash_can_for_request(request)

        return super().get_queryset(request).prefetch_related("page")


modeladmin_register(TrashCanModelAdmin)


@hooks.register("before_bulk_action")
def delete_bulk_pages(request, action_type, objects, action_class_instance):
    if action_type == "delete" and isinstance(action_class_instance, DeleteBulkAction):
        return trash_bulk_delete(request, objects)
    return None


@hooks.register("before_delete_page")
def delete_page(request, page):
    return trash_delete(request, page)


@hooks.register("construct_page_chooser_queryset")
def exclude_trash_can_from_chooser(pages, request):
    return pages.not_type(TrashCanPage)


@hooks.register("construct_explorer_page_queryset")
def exclude_trash_can_from_explorer(parent_page, pages, request):
    return pages.not_type(TrashCanPage)


@hooks.register("register_admin_urls")
def urlconf_time():
    return [
        path(
            "wagtail_trash/restore_and_move/<int:page_id>/",
            trash_move,
            name="wagtail_trash_move",
        ),
        path(
            "wagtail_trash/restore/<int:page_id>/",
            trash_restore,
            name="wagtail_trash_restore",
        ),
    ]
