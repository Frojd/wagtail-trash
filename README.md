# wagtail recycle bin

Instead of deleting pages when pressing delete, pages will get thrown into the "Recycle Bin".


## Install

First install the python package:
`pip install wagtail-recycle-bin`

Then add it to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "wagtail_recycle_bin",
]
```

Run migrations, et voila!


## How it works

Wagtail Recycle Bin works by hooking into the Wagtail hook `before_delete_page` and overriding the delete view.
Instead of deleting the page the page gets moved to the special "Recycle Bin" page. The deleted page and all descendants will get unpublished.
From the recycle bin in Wagtail admin it's then possible to permanently delete the page or to restore the page. Restoring a page will also republish the pages that were published when getting deleted.
If the parent of the deleted page is either in the recycle bin or permanently deleted it's still possible to restore the pages by supplying an alternate parent.


## Caveats

Since Wagtail Recycle Bin uses the hook `before_delete_page` it might interfere with your applications `before_delete_page` if you have defined one that returns a status code. Make sure wagtail recycle bin is the last hook that runs otherwise or your custom `before_delete_page` might not run since Wagtail Recycle Bin doesn't call it.

Also, Wagtail Recycle Bin "deletes" pages by unpublishing them, so if you use a queryset that doesn't filter out unpublished pages recycled pages might show up. There is a manager that will fix this for you included, example:

```python
from wagtail_recycle_bin.managers import RecycleManager

class SomePage(Page):
    objects_excluding_bins = RecycleManager()

# Now you can do this without getting any pages from the bin:
SomePage.objects_excluding_bins.all()
```

Permissions: If you remove a page under a restricted area, this page will be moved and therefore get new permissions. A user might go from not being allowed to see pages under e.g. "Secret Page", but when a page under this area is moved to recycle bin, the permissions from "Secret Page" are gone so now the user will see it in the recycle bin.
This is a solvable issue and will be fixed in a later version.


## Clearing the bin regularly

There is an included managment-command called `empty_recycle_bin` that takes a required argument `--older_than_days`. To remove all items in the bin that's been there more than 30 days run this command:

`./manage.py empty_recycle_bin --older_than_days=30`


## Todo

- Make sure page permissions are respected in the recycle bin.
