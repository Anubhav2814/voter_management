from django import forms
from .models import VoterField
from .models import Voter


class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional by default
        for field in self.fields:
            self.fields[field].required = False

        # Set required fields
        required_fields = ['mlc_constituency', 'assembly', 'mandal', 'sno', 'mobile_no']
        for field_name in required_fields:
            self.fields[field_name].required = True

class VoterFieldForm(forms.ModelForm):
    class Meta:
        model = VoterField
        fields = ['name', 'field_type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter field name'
            }),
            'field_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].upper()
        if VoterField.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A field with this name already exists.')
        return name

