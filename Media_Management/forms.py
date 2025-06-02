from django import forms
from .models import Media
from ckeditor.widgets import CKEditorWidget
import json


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class MediaForm(forms.ModelForm):
    multiple_images = MultipleFileField(
        required=False,
        help_text="Select multiple images at once"
    )

    multiple_video_links = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter multiple video URLs, one per line\nExample:\nhttps://www.youtube.com/watch?v=VIDEO_ID1\nhttps://vimeo.com/VIDEO_ID2'
        }),
        required=False,
        help_text="Enter multiple video URLs, one per line"
    )

    class Meta:
        model = Media
        fields = [
            'title',
            'media_type',
            'image',
            'multiple_images',
            'video_link',
            'multiple_video_links',
            'caption',
            'category',
            'tags',
            'status'
        ]
        widgets = {
            'caption': CKEditorWidget(),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Enter tags separated by commas'
            }),
            'video_link': forms.URLInput(attrs={
                'placeholder': 'Enter single YouTube or Vimeo video URL'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing existing media, populate multiple fields
        if self.instance and self.instance.pk:
            if self.instance.video_links:
                self.fields['multiple_video_links'].initial = '\n'.join(self.instance.video_links)

    def clean_multiple_video_links(self):
        video_links_text = self.cleaned_data.get('multiple_video_links', '')
        if not video_links_text.strip():
            return []

        video_links = [link.strip() for link in video_links_text.split('\n') if link.strip()]

        # Validate each video link
        for link in video_links:
            if not ('youtube.com' in link or 'youtu.be' in link or 'vimeo.com' in link):
                raise forms.ValidationError(f'Invalid video URL: {link}. Only YouTube and Vimeo links are supported.')

        return video_links

    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')
        image = cleaned_data.get('image')
        multiple_images = cleaned_data.get('multiple_images')
        video_link = cleaned_data.get('video_link')
        multiple_video_links = cleaned_data.get('multiple_video_links')

        if media_type == 'image':
            if not image and not multiple_images:
                self.add_error('multiple_images', 'At least one image is required for image media type.')
        elif media_type == 'video':
            if not video_link and not multiple_video_links:
                self.add_error('multiple_video_links', 'At least one video link is required for video media type.')
        elif media_type == 'mixed':
            has_images = image or multiple_images
            has_videos = video_link or multiple_video_links
            if not has_images and not has_videos:
                self.add_error('multiple_images', 'At least one image or video is required for mixed media type.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle multiple images
        multiple_images = self.cleaned_data.get('multiple_images')
        if multiple_images:
            # Store image URLs/paths in JSON field
            image_urls = []
            for image_file in multiple_images:
                # Save each image and store the URL
                # You might want to use a proper file storage solution
                image_urls.append(image_file.name)  # Simplified - you'll need proper file handling
            instance.images = image_urls

        # Handle multiple video links
        multiple_video_links = self.cleaned_data.get('multiple_video_links')
        if multiple_video_links:
            instance.video_links = multiple_video_links

        if commit:
            instance.save()
        return instance
