from django.contrib import admin
from django.urls import path
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from django.urls import reverse
from .models import Media
from .forms import MediaForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    form = MediaForm

    list_display = (
        'title',
        'author',
        'media_type',
        'category',
        'status',
        'format_created_at',
        'created_by',
        'display_actions'  # Make sure this is included
    )

    search_fields = ('title', 'caption', 'author__username', 'created_by')
    list_filter = []  # Remove sidebar filters

    readonly_fields = (
        'slug',
        'created_at',
        'updated_at',
        'created_by',
        'created_time'
    )

    fieldsets = (
        ('Content', {
            'fields': (
                'title',
                'media_type',
                'image',
                'video_link',
                'caption',
            ),
        }),
        ('Classification', {
            'fields': (
                'category',
                'status',
                'tags'
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                'created_time',
                'created_at',
                'updated_at',
                'slug'
            ),
            'classes': ('collapse',)
        }),
    )

    def display_actions(self, obj):
        """Generate action buttons for each row"""
        if obj and hasattr(obj, 'pk') and obj.pk:
            edit_url = reverse('admin:Media_Management_media_change', args=[obj.pk])
            preview_url = reverse('admin:media_preview', args=[obj.pk])
            return format_html(
                '<div class="action-buttons">'
                '<a class="action-btn edit-btn" href="{}" title="Edit">'
                '<i class="fas fa-edit"></i> Edit</a> '
                '<a class="action-btn preview-btn" href="{}" target="_blank" title="Preview">'
                '<i class="fas fa-eye"></i> Preview</a> '
                '<button onclick="archiveMedia({})" class="action-btn archive-btn" title="Archive">'
                '<i class="fas fa-archive"></i> Archive</button>'
                '</div>',
                edit_url, preview_url, obj.pk
            )
        return ""

    display_actions.short_description = 'Actions'
    display_actions.allow_tags = True

    def format_created_at(self, obj):
        """Format the created_at date in the specified format"""
        if obj.created_at:
            return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return "-"

    format_created_at.short_description = 'Created At'
    format_created_at.admin_order_field = 'created_at'

    @method_decorator(csrf_exempt)
    def archive_media(self, request, pk):
        """Archive media item"""
        try:
            media = get_object_or_404(Media, pk=pk)
            media.status = 'archived'
            media.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Media archived successfully',
                'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    def preview_media(self, request, pk):
        """Preview view for media items"""
        media = get_object_or_404(Media, pk=pk)
        context = {
            'media': media,
            'title': f'Preview: {media.title}',
            'is_popup': True,
            'has_permission': True,
            'site_header': self.admin_site.site_header,
            'site_title': self.admin_site.site_title,
            'opts': self.model._meta,
        }
        return render(request, 'admin/Media_Management/media/preview.html', context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/preview/',
                self.admin_site.admin_view(self.preview_media),
                name='media_preview',
            ),
            path(
                '<int:pk>/archive/',
                self.admin_site.admin_view(self.archive_media),
                name='media_archive',
            ),
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        """Handle saving the model and setting automatic fields"""
        if not change:  # If creating new object
            obj.author = request.user
            obj.created_by = request.user.username
            obj.created_time = timezone.now()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Custom queryset to handle filters"""
        qs = super().get_queryset(request)

        # Get filter parameters from request
        status = request.GET.get('status')
        media_type = request.GET.get('media_type')
        category = request.GET.get('category')

        # Apply filters if they exist
        if status:
            qs = qs.filter(status=status)
        if media_type:
            qs = qs.filter(media_type=media_type)
        if category:
            qs = qs.filter(category=category)

        return qs

    def changelist_view(self, request, extra_context=None):
        """Add extra context to the changelist view"""
        extra_context = extra_context or {}

        # Add current datetime and user
        extra_context['current_datetime'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        extra_context['user_login'] = request.user.username

        # Add filter choices
        extra_context['status_choices'] = Media.STATUS_CHOICES
        extra_context['media_type_choices'] = Media.MEDIA_TYPE_CHOICES
        extra_context['category_choices'] = Media.CATEGORY_CHOICES

        # Add current filter values
        extra_context['current_status'] = request.GET.get('status', '')
        extra_context['current_media_type'] = request.GET.get('media_type', '')
        extra_context['current_category'] = request.GET.get('category', '')

        return super().changelist_view(request, extra_context=extra_context)


