from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls", namespace="core")),
    path("", include("apps.catalog.urls", namespace="catalog")),
    path(settings.ADMIN_URL, include("apps.dashboard.urls", namespace="dashboard")),
    path("django-admin/", admin.site.urls),
]

if settings.DEBUG or getattr(settings, "SERVE_MEDIA_FILES", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
