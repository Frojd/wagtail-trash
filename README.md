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


## Clearing the bin regularly

There is an included managment-command called `empty_recycle_bin` that takes a required argument `--older_than_days`. To remove all items in the bin that's been there more than 30 days run this command:

`./manage.py empty_recycle_bin --older_than_days=30`
