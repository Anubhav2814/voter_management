from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ..models import Media
from .serializers import MediaSerializer, MediaListSerializer

class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = []  # Remove any permission classes
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'list':
            return MediaListSerializer
        return MediaSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by="Anonymous",  # Default to Anonymous since there's no authentication
            created_time=timezone.now()
        )

    def get_queryset(self):
        queryset = Media.objects.all()
        status_param = self.request.query_params.get('status', None)
        category = self.request.query_params.get('category', None)
        media_type = self.request.query_params.get('media_type', None)

        if status_param:
            queryset = queryset.filter(status=status_param)
        if category:
            queryset = queryset.filter(category=category)
        if media_type:
            queryset = queryset.filter(media_type=media_type)

        return queryset

    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def archive(self, request, pk=None):
        try:
            media = self.get_object()
            media.status = 'archived'
            media.save()
            return Response({
                'status': 'success',
                'message': 'Media archived successfully',
                'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        media = self.get_object()
        media.status = 'published'
        media.published_date = timezone.now()
        media.save()
        return Response({
            'status': 'success',
            'message': 'Media published successfully',
            'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        media = self.get_object()
        serializer = self.get_serializer(media)
        return Response(serializer.data)