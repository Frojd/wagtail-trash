import json
from wagtail.core.models import Site, Page
from .models import TrashCanPage


def trash_can_for_request(request):
    site = Site.find_for_request(request)
    trash_can = TrashCanPage.objects.in_site(site)

    if not trash_can.exists():
        trash_can = TrashCanPage(
            title="Trash Can",
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

    rb.page.move(move_to_page, pos="first-child", user=request.user)

    to_be_published_ids = json.loads(rb.data)["published"]

    to_publish_pages = Page.objects.filter(id__in=to_be_published_ids)

    for page in to_publish_pages:
        # Should we make a revision here instead?
        page.has_unpublished_changes = False
        page.live = True
        page.save()

    rb.delete()
