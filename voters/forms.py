from django import forms
from .models import VoterField, Voter

class VoterForm(forms.ModelForm):
    """
    Form for creating and editing Voter objects.
    """
    class Meta:
        model = Voter
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False  # Make all fields optional by default
        required_fields = ['mlc_constituency', 'assembly', 'mandal', 'sno', 'mobile_no']
        for field_name in required_fields:
            self.fields[field_name].required = True  # Set specific fields as required

class VoterFieldForm(forms.ModelForm):
    """
    Form for creating and editing VoterField objects.
    """
    class Meta:
        model = VoterField
        fields = ['name', 'field_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter field name'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        """
        Validates that the field name is unique.
        """
        name = self.cleaned_data['name'].upper()
        if VoterField.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A field with this name already exists.')
        return name