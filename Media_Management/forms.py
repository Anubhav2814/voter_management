from django import forms
from .models import Media
from ckeditor.widgets import CKEditorWidget

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = [
            'title',
            'media_type',
            'image',
            'video_link',
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
                'placeholder': 'Enter YouTube or Vimeo video URL'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')
        image = cleaned_data.get('image')
        video_link = cleaned_data.get('video_link')

        if media_type == 'image' and not image:
            self.add_error('image', 'An image file is required for image Media_Management type.')
        elif media_type == 'video' and not video_link:
            self.add_error('video_link', 'A video link is required for video Media_Management type.')

        if media_type == 'video' and video_link:
            if not ('youtube.com' in video_link or 'youtu.be' in video_link or 'vimeo.com' in video_link):
                self.add_error('video_link', 'Only YouTube and Vimeo links are supported.')

        return cleaned_data