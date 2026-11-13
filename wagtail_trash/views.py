from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from treebeard.mp_tree import MP_MoveHandler
from wagtail.admin import messages
from wagtail.models import Page

from .forms import MoveForm
from .models import TrashCan
from .utils import (
    RestoreError,
    generate_page_data,
    restore_and_move_page,
    trash_can_for_request,
)


def get_valid_next_url_from_request(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if not next_url or not url_has_allowed_host_and_scheme(
        url=next_url, allowed_hosts={request.get_host()}
    ):
        return ""
    return next_url


def trash_bulk_delete(request, pages):
    trash_can = trash_can_for_request(request)
    parent_ids = set()

    for page in pages:
        parent = page.get_parent()
        parent_ids.add(parent.id)

        if parent.id == trash_can.id:
            page.delete(user=request.user)

            messages.success(
                request, _("Page '{0}' deleted.").format(page.get_admin_display_title())
            )
        else:
            TrashCan.objects.create(
                page=page,
                parent=parent,
                user=request.user,
                data=generate_page_data(page),
            )

            page.slug = f"trash-{page.id}-{page.slug}"
            page.save()
            page.get_descendants(inclusive=True).unpublish()

            # Preserve the url path
            old_page = Page.objects.get(id=page.id)
            new_url_path = old_page.set_url_path(parent=trash_can)

            MP_MoveHandler(page, trash_can, "first-child").process()

            # And reset the url path when in trash
            new_page = Page.objects.get(id=page.id)
            new_page.url_path = new_url_path
            new_page.save()

    next_url = get_valid_next_url_from_request(request)

    if next_url:
        return redirect(next_url)

    if len(parent_ids) == 1:
        return redirect("wagtailadmin_explore", parent_ids.pop())

    return redirect("wagtailadmin_explore_root")


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

        page.slug = f"trash-{page.id}-{page.slug}"
        page.save()
        page.get_descendants(inclusive=True).unpublish()

        # Preserve the url path
        old_page = Page.objects.get(id=page.id)
        new_url_path = old_page.set_url_path(parent=trash_can)

        MP_MoveHandler(page, trash_can, "first-child").process()

        # And reset the url path when in trash
        new_page = Page.objects.get(id=page.id)
        new_page.url_path = new_url_path
        new_page.save()

        messages.success(
            request,
            _("Page '{0}' moved to trash_can.").format(page.get_admin_display_title()),
        )

    next_url = get_valid_next_url_from_request(request)

    if next_url:
        return redirect(next_url)

    return redirect("wagtailadmin_explore", parent.id)


def trash_move(request, page_id):
    rb = get_object_or_404(TrashCan, page_id=page_id)

    if request.method == "POST":
        form = MoveForm(data=request.POST)
        if not form.is_valid():
            return render(
                request,
                "wagtail_trash/move.html",
                {
                    "form": form,
                },
            )

        move_to_page = form.cleaned_data["move_page"]

        try:
            restore_and_move_page(rb, move_to_page, request)
        except RestoreError as e:
            form.add_error("move_page", str(e))
            return render(request, "wagtail_trash/move.html", {"form": form})

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


def trash_restore(request, page_id):
    rb = get_object_or_404(TrashCan, page_id=page_id)
    page = rb.page

    if request.method != "POST":
        return render(
            request, "wagtail_trash/restore.html", {"page": page, "parent": rb.parent}
        )

    try:
        restore_and_move_page(rb, rb.parent, request)
    except RestoreError as e:
        messages.error(
            request,
            _("Page '{0}' could not be restored. {1}").format(
                page.get_admin_display_title(), e
            ),
        )
        return redirect("wagtail_trash_move", page_id)

    messages.success(
        request,
        _("Page '{0}' successfully restored.").format(page.get_admin_display_title()),
    )

    return redirect("wagtailadmin_explore", page_id)
