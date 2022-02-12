import json

from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from wagtail.admin import messages
from wagtail.admin.views.pages import delete
from wagtail.core import hooks
from wagtail.core.models import Page, Site

from .forms import MoveForm
from .models import TrashCan, TrashCanPage
from .utils import generate_page_data, restore_and_move_page, trash_can_for_request


def get_valid_next_url_from_request(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if not next_url or not url_has_allowed_host_and_scheme(
        url=next_url, allowed_hosts={request.get_host()}
    ):
        return ""
    return next_url


def trash_delete(request, page):
    if not request.method == "POST":
        return

    trash_can = trash_can_for_request(request)

    parent = page.get_parent()

    if parent.id == trash_can.id:
        page.delete(user=request.user)

        messages.success(
            request, _("Page '{0}' deleted.").format(page.get_admin_display_title())
        )
    else:
        TrashCan.objects.create(
            page=page, parent=parent, user=request.user, data=generate_page_data(page)
        )

        page.get_descendants(inclusive=True).unpublish()
        page.move(trash_can, pos="first-child", user=request.user)

        messages.success(
            request,
            _("Page '{0}' moved to trash_can.").format(page.get_admin_display_title()),
        )

    next_url = get_valid_next_url_from_request(request)

    if next_url:
        return redirect(next_url)

    return redirect("wagtailadmin_explore", parent.id)


def trash_move(request, page_id):
    if request.method == "POST":
        rb = TrashCan.objects.get(page_id=page_id)
        move_to_page = Page.objects.get(pk=request.POST.get("move_page"))
        restore_and_move_page(rb, move_to_page, request)

        messages.success(
            request,
            _("Page '{0}' successfully restored.").format(
                rb.page.get_admin_display_title()
            ),
        )

        return redirect("wagtailadmin_explore", rb.page_id)

    return render(
        request,
        "wagtail_trash/move.html",
        {
            "form": MoveForm(),
        },
    )


def trash_restore(request, page_id, move_to_id=None):
    rb = TrashCan.objects.get(page_id=page_id)
    page = rb.page

    if not page.permissions_for_user(request.user).can_edit():
        raise PermissionDenied

    restore_and_move_page(rb, rb.parent, request)

    messages.success(
        request,
        _("Page '{0}' successfully restored.").format(page.get_admin_display_title()),
    )

    return redirect("wagtailadmin_explore", page_id)
