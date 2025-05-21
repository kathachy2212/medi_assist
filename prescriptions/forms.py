from django import forms
from .models import Disease,ChatMessage

class DiseaseForm(forms.ModelForm):
    class Meta:
        model = Disease
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter disease name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter disease description'}),
        }
        

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        labels = {
            'message': 'Your Message',
        }

    def __init__(self, *args, **kwargs):
        super(ChatMessageForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'