import wagtail.admin.urls
import wagtail.core.urls
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, re_path

urlpatterns = [
    re_path(r"^admin/", include(wagtail.admin.urls)),
    re_path(r"", include(wagtail.core.urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
