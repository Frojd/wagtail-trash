from django.utils.http import is_safe_url
from django.utils.translation import gettext as _
from django.shortcuts import redirect
from wagtail.core.models import Site
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
