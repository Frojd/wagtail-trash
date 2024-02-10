[![Run tests, lint and publish](https://github.com/Frojd/wagtail-trash/actions/workflows/main.yml/badge.svg)](https://github.com/Frojd/wagtail-trash/actions/workflows/main.yml) [![PyPI version](https://badge.fury.io/py/wagtail-trash.svg)](https://badge.fury.io/py/wagtail-trash)

# wagtail trash

Instead of deleting pages when pressing delete, pages will get thrown into the "Trash Can".


## Install

1. First install the python package:
`pip install wagtail-trash`

This step will install both `wagtail-trash` and `wagtail-modeladmin` which is a requirement for the admin.

2. Then add both `wagtail-trash` and `wagtail-modeladmin` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "wagtail_modeladmin",
    "wagtail_trash",
]
```

3. Run migrations, et voila!


## How it works

Wagtail Trash works by hooking into the Wagtail hook `before_delete_page` and overriding the delete view.
Instead of deleting the page the page gets moved to the special "Trash" page. The deleted page and all descendants will get unpublished.
From the trash can in Wagtail admin it's then possible to permanently delete the page or to restore the page. Restoring a page will also republish the pages that were published when getting deleted.
If the parent of the deleted page is either in the trash can or permanently deleted it's still possible to restore the pages by supplying an alternate parent.


## Caveats

Since Wagtail Trash uses the hook `before_delete_page` it might interfere with your applications `before_delete_page` if you have defined one that returns a status code. Make sure wagtail trash is the last hook that runs otherwise or your custom `before_delete_page` might not run since Wagtail Trash doesn't call it.

Also, Wagtail Trash "deletes" pages by unpublishing them, so if you use a queryset that doesn't filter out unpublished pages, pages in trash can might show up. There is a manager that will fix this for you included, example:

```python
from wagtail.core.models import Page, PageManager
from wagtail_trash.managers import TrashManager

class SomePage(Page):
    objects = PageManager()  # needed, so _default_manager isn't the trash manager
    objects_excluding_trash = TrashManager()

# Now you can do this without getting any pages from the bin:
SomePage.objects_excluding_trash.all()
```

Permissions: If you remove a page under a restricted area, this page will be moved and therefore get new permissions. A user might go from not being allowed to see pages under e.g. "Secret Page", but when a page under this area is moved to trash can, the permissions from "Secret Page" are gone so now the user will see it in the trash can.
This is a solvable issue and will be fixed in a later version.


## Clearing the bin regularly

There is an included managment-command called `empty_trash` that takes a required argument `--older_than_days`. To remove all items in the bin that's been there more than 30 days run this command:

`./manage.py empty_trash --older_than_days=30`

## Git flow

This project uses git flow, current release is in the `main` branch and the current development is in the `develop` branch.


## License

wagtail trash is released under the [MIT License](http://www.opensource.org/licenses/MIT).
