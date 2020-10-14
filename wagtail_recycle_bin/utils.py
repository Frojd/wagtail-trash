import json
from wagtail.core.models import Site
from .models import RecycleBinPage


def recycle_bin_for_request(request):
    site = Site.find_for_request(request)
    recycle_bin = RecycleBinPage.objects.in_site(site)

    if not recycle_bin.exists():
        recycle_bin = RecycleBinPage(
            title="Recycle bin",
            has_unpublished_changes=True,
            live=False,
        )
        site.root_page.add_child(instance=recycle_bin)
        recycle_bin.save_revision()
    else:
        recycle_bin = recycle_bin.first()

    return recycle_bin


def generate_page_data(page):
    id_list = []

    if page.live:
        id_list.append(page.id)

    id_list.extend(page.get_descendants().live().values_list("id", flat=True))

    data = {
        "published": id_list,
    }

    return json.dumps(data)
