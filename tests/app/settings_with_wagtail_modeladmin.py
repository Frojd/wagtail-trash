from .settings import *  # noqa: F403

INSTALLED_APPS = [
    "wagtail_modeladmin" if x == "wagtail.contrib.modeladmin" else x
    for x in INSTALLED_APPS
]
