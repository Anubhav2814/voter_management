from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('voters/', include('voters.urls')),
    # path('', include('voters.urls')),
    path('notifications/', include('notifications.urls')),
    path('', include('passes.urls')),
    path('news/', include('news.urls')),
    path('', include('blogs.urls')),
    # path('api/', include('blogs.api.urls')),
    path('', include('Media_Management.urls')),
    path('events/', include('events.urls')),
    # path('api/', include('Media_Management.urls')),
    path('invitations/', include('invitations.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
admin.site.site_header = 'Voter Management System'
admin.site.site_title = 'Voter Management'
admin.site.index_title = 'Welcome to Voter Management System'