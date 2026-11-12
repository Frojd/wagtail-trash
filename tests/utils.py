from django.shortcuts import reverse


def trash_page(client, page, **extra):
    return client.post(reverse("wagtailadmin_pages:delete", args=(page.id,)), **extra)
