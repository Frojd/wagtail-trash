import wagtail.admin.urls
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, re_path
from wagtail import urls as wagtail_urls

urlpatterns = [
    re_path(r"^admin/", include(wagtail.admin.urls)),
    re_path(r"", include(wagtail_urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
