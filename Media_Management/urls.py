from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = 'Media_Management'

urlpatterns = [
    # Include API URLs
    path('api/', include('Media_Management.api.urls', namespace='media_api')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)