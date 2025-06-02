from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils import timezone
import uuid
import json


class Media(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    )

    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('mixed', 'Mixed (Images & Videos)')
    )

    CATEGORY_CHOICES = (
        ('event', 'Event Photos'),
        ('campaign', 'Campaign Videos'),
        ('interview', 'Interviews'),
        ('behind_scenes', 'Behind-the-Scenes')
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        editable=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Media_Management'
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)

    # Multiple images field - stored as JSON
    images = models.JSONField(default=list, blank=True, help_text="Multiple image files")

    # Multiple video links field - stored as JSON
    video_links = models.JSONField(default=list, blank=True, help_text="Multiple video URLs")

    # Keep original fields for backward compatibility
    image = models.ImageField(upload_to='media_images/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)

    caption = RichTextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tags = models.CharField(max_length=200, blank=True, help_text="Enter tags separated by commas")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=100, default='swastik404-ai', editable=False)
    created_time = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Media'
        verbose_name_plural = 'Media'

    def __str__(self):
        return self.title

    def generate_unique_slug(self):
        base_slug = slugify(self.title)
        unique_slug = base_slug
        while Media.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        if not self.created_by:
            self.created_by = 'swastik404-ai'
        if not self.created_time:
            self.created_time = timezone.now()
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)

    def clean(self):
        if self.media_type == 'image' and not self.images and not self.image:
            raise ValidationError('At least one image is required for image media type')
        if self.media_type == 'video' and not self.video_links and not self.video_link:
            raise ValidationError('At least one video link is required for video media type')
        if self.media_type == 'mixed' and not self.images and not self.video_links and not self.image and not self.video_link:
            raise ValidationError('At least one image or video is required for mixed media type')

    def get_all_images(self):
        """Get all images including single image and multiple images"""
        all_images = []
        if self.image:
            all_images.append(self.image.url)
        if self.images:
            all_images.extend(self.images)
        return all_images

    def get_all_videos(self):
        """Get all video links including single video and multiple videos"""
        all_videos = []
        if self.video_link:
            all_videos.append(self.video_link)
        if self.video_links:
            all_videos.extend(self.video_links)
        return all_videos
