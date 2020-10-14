import json
from django.utils.http import is_safe_url
from django.utils.translation import gettext as _
from django.shortcuts import redirect
from wagtail.core.models import Site, Page
from wagtail.core import hooks
from wagtail.admin import messages
from wagtail.admin.views.pages import delete
from .models import RecycleBinPage, RecycleBin
from .utils import recycle_bin_for_request, generate_page_data


def get_valid_next_url_from_request(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if not next_url or not is_safe_url(
        url=next_url, allowed_hosts={request.get_host()}
    ):
        return ""
    return next_url


def recycle_delete(request, page):
    recycle_bin = recycle_bin_for_request(request)

    parent = page.get_parent()

    if parent.id == recycle_bin.id:
        page.delete(user=request.user)

        messages.success(
            request, _("Page '{0}' deleted.").format(page.get_admin_display_title())
        )
    else:
        RecycleBin.objects.create(
            page=page, parent=parent, user=request.user, data=generate_page_data(page)
        )

        page.get_descendants(inclusive=True).unpublish()
        page.move(recycle_bin, pos="first-child", user=request.user)

        messages.success(
            request,
            _("Page '{0}' moved to recycle bin.").format(
                page.get_admin_display_title()
            ),
        )

    next_url = get_valid_next_url_from_request(request)

    if next_url:
        return redirect(next_url)

    return redirect("wagtailadmin_explore", parent.id)


def recycle_restore(request, page_id):
    rb = RecycleBin.objects.get(page_id=page_id)

    page = rb.page
    page.move(rb.parent, pos="first-child", user=request.user)

    to_be_published_ids = json.loads(rb.data)["published"]

    to_publish_pages = Page.objects.filter(id__in=to_be_published_ids)

    for page in to_publish_pages:
        # Should we make a revision here instead?
        page.has_unpublished_changes = False
        page.live = True
        page.save()

    rb.delete()

    return redirect("wagtailadmin_explore", page_id)
