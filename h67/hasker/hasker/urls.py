from django.conf import settings
from django.urls import re_path, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('askme.urls')),
    re_path(r'^', include('hasker_user.urls')),
    # re_path(r'^api/v1/', include(router.urls)),
    re_path(r'^api/v1/', include('api.urls')),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)