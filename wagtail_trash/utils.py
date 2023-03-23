import json
import re

from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from wagtail.actions.move_page import MovePageAction
from wagtail.models import Page, Site

from .models import TrashCanPage


def trash_can_for_request(request):
    site = Site.find_for_request(request)
    trash_can = TrashCanPage.objects.in_site(site)

    if not trash_can.exists():
        trash_can = TrashCanPage(
            title=_("Trash Can"),
            has_unpublished_changes=True,
            live=False,
        )
        site.root_page.add_child(instance=trash_can)
        trash_can.save_revision()
    else:
        trash_can = trash_can.first()

    return trash_can


def generate_page_data(page):
    id_list = []

    if page.live:
        id_list.append(page.id)

    id_list.extend(page.get_descendants().live().values_list("id", flat=True))

    data = {
        "published": id_list,
    }

    return json.dumps(data)


def restore_and_move_page(rb, move_to_page, request):
    if not rb.page.permissions_for_user(request.user).can_move():
        raise PermissionDenied

    rb.page.slug = re.sub(r"trash-\d+-", "", rb.page.slug)
    rb.page.save()

    action = MovePageAction(rb.page, move_to_page, pos="first-child", user=request.user)
    action.execute(skip_permission_checks=True)

    to_be_published_ids = json.loads(rb.data)["published"]

    to_publish_pages = Page.objects.filter(id__in=to_be_published_ids)

    for page in to_publish_pages:
        # Should we make a revision here instead?
        page.has_unpublished_changes = False
        page.live = True
        page.save()

    rb.delete()
