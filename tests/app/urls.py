import wagtail.admin.urls
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail import urls as wagtail_urls
else:
    from wagtail.core import urls as wagtail_urls
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, re_path

urlpatterns = [
    re_path(r"^admin/", include(wagtail.admin.urls)),
    re_path(r"", include(wagtail_urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
