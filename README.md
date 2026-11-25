[![CI](https://github.com/Frojd/wagtail-trash/actions/workflows/ci.yml/badge.svg)](https://github.com/Frojd/wagtail-trash/actions/workflows/ci.yml) [![PyPI version](https://badge.fury.io/py/wagtail-trash.svg)](https://badge.fury.io/py/wagtail-trash)

# wagtail trash

Instead of deleting pages when pressing delete, pages will get thrown into the "Trash Can".


## Features

- Deleted pages are moved to a trash can instead of being removed, this includes bulk delete from the page explorer
- Restore pages to their original parent, or restore and move them to a new parent
- Pages that were live when deleted are republished on restore
- Permanently delete pages from the trash can in Wagtail admin
- One trash can per site, hidden from the page explorer and page chooser
- `TrashManager` for querysets that should exclude trashed pages
- `SkipSitemapIfInTrashMixin` to keep trashed pages out of the sitemap
- Management commands to empty the trash and clean up stray pages
- Translations for English, Spanish (Argentina), Portuguese (Brazil) and Swedish


## Requirements

- Python 3.11, 3.12, 3.13, 3.14, 3.15
- Django 5.2, 6.0, 6.1
- Wagtail 7.4, 8.0, 8.1
- wagtail-modeladmin 2.5 or newer

Django 6.0 and 6.1 require Python 3.12 or newer, Python 3.15 requires Django 6.1 and Wagtail 8.1, and Wagtail 7.4 supports Django 5.2 and 6.0 only.


## Install

1. First install the python package:
`pip install wagtail-trash`

This step will install both `wagtail-trash` and `wagtail-modeladmin` which is a requirement for the admin.

2. Then add both `wagtail_trash` and `wagtail_modeladmin` to your `INSTALLED_APPS`, after your own apps (see [App order](#app-order)):

```python
INSTALLED_APPS = [
    # ...
    "wagtail_modeladmin",
    "wagtail_trash",
]
```

3. Run migrations:

```
python manage.py migrate
```


## How it works

Wagtail Trash works by hooking into the Wagtail hook `before_delete_page` and overriding the delete view.
Instead of deleting the page the page gets moved to the special "Trash" page. The deleted page and all descendants will get unpublished.
From the trash can in Wagtail admin it's then possible to permanently delete the page or to restore the page. Restoring a page will also republish the pages that were published when getting deleted.
If the parent of the deleted page is either in the trash can or permanently deleted it's still possible to restore the pages by supplying an alternate parent.


## Usage

### App order
Wagtail Trash uses the `before_delete_page` and `before_bulk_action` hooks and returns a response from them. Wagtail stops running hooks once one returns a response, so any of your own `before_delete_page` or `before_bulk_action` hooks registered after Wagtail Trash will not run. Hooks run in `INSTALLED_APPS` order, so place `wagtail_trash` after your own apps.

```python
# Example
INSTALLED_APPS = [
    "wagtail.sites",
    "wagtail",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail_modeladmin",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.settings",
    "wagtail_trash",  # Import here
    ...
]
```

### Page manager
Pages in the trash can are unpublished, so querysets filtered with `.live()` already exclude them. Querysets that include unpublished pages will return trashed pages too. `TrashManager` excludes every page placed under a trash can, example:

```python
from wagtail.models import Page, PageManager
from wagtail_trash.managers import TrashManager

class SomePage(Page):
    objects = PageManager()  # needed, so _default_manager isn't the trash manager
    objects_excluding_trash = TrashManager()

# Now you can do this without getting any pages from the bin:
SomePage.objects_excluding_trash.all()
```

### Exclude from sitemap
Add SkipSitemapIfInTrashMixin if you want trashed pages to be excluded from sitemap.

```python
from wagtail.models import Page
from wagtail_trash.mixins import SkipSitemapIfInTrashMixin

class SomePage(SkipSitemapIfInTrashMixin, Page):
    ...
```

### Restoring pages
Restoring a page requires add and publish permission on the destination page. Page type rules such as `parent_page_types` and `max_count_per_parent` are enforced, and pages cannot be restored into a parent that is itself in the trash can. If the original parent is in the trash can or has been deleted, use "Restore and move" to pick a new parent.


## Clearing the bin regularly

The included management command `empty_trash` takes a required argument `--older_than_days`. Pages are permanently deleted. To remove all pages that have been in the bin for more than 30 days, run:

```
./manage.py empty_trash --older_than_days=30
```


## Known limitations

### Permissions
Moving a page to the trash can changes its place in the page tree, so it no longer inherits permissions from its original parent. A user who could not see pages under e.g. "Secret Page" can see a page from that area once it is in the trash can.

## Git flow

This project uses git flow, current release is in the `main` branch and the current development is in the `develop` branch.


## License

wagtail trash is released under the [MIT License](http://www.opensource.org/licenses/MIT).
