from rest_framework import serializers
from ..models import Media

class MediaSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = [
            'id', 'title', 'slug', 'media_type', 'image', 'video_link',
            'caption', 'category', 'tags', 'status', 'created_at',
            'author_name', 'published_date'
        ]
        read_only_fields = ['slug', 'author_name', 'published_date']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

class MediaListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ['id', 'title', 'slug', 'media_type', 'media_url', 'category', 'status', 'created_at', 'author_name']
        read_only_fields = ['slug', 'author_name']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def get_media_url(self, obj):
        if obj.media_type == 'image':
            return obj.image.url if obj.image else None
        return obj.video_link