from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MediaViewSet

app_name = 'media_api'

router = DefaultRouter()
router.register(r'Media_Management', MediaViewSet, basename='Media_Management')

urlpatterns = [
    path('', include(router.urls)),
]
