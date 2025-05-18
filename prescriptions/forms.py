from django import forms
from .models import Disease

class DiseaseForm(forms.ModelForm):
    class Meta:
        model = Disease
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter disease name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter disease description'}),
        }