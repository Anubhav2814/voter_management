from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils import timezone
import uuid

class Media(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    )

    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video')
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
    image = models.ImageField(upload_to='media_images/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)
    caption = RichTextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tags = models.CharField(max_length=200, blank=True, help_text="Enter tags separated by commas")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=100, default='swastik404-ai', editable=False)  # Set default to current user
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
            self.created_by = 'Administrator'  # Set default user

        if not self.created_time:
            self.created_time = timezone.now()

        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()

        super().save(*args, **kwargs)

    def clean(self):
        if self.media_type == 'image' and not self.image:
            raise ValidationError('Image file is required for image Media_Management type')
        if self.media_type == 'video' and not self.video_link:
            raise ValidationError('Video link is required for video Media_Management type')