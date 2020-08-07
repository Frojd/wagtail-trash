import wagtail.admin.urls
import wagtail.core.urls
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static


urlpatterns = [
    url(r"^admin/", include(wagtail.admin.urls)),
    url(r"", include(wagtail.core.urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
