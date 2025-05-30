from django import forms
from django.forms import modelformset_factory
from .models import Disease, ChatMessage,ChatResponseSuggestion,SymptomMedicine

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
        fields = ['message', 'is_bot']
        labels = {
            'message': 'Your Message',
            'is_bot': 'Send as Bot',
        }

    def __init__(self, *args, **kwargs):
        super(ChatMessageForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Don't apply 'form-control' to checkboxes
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
                
                
class ChatResponseSuggestionForm(forms.ModelForm):
    class Meta:
        model = ChatResponseSuggestion
        fields = ['text']
        labels = {
            'text': 'Possible Answer',
        }
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter possible answer'}),
        }
        
        
class SymptomMedicineForm(forms.ModelForm):
    class Meta:
        model = SymptomMedicine
        fields = ['symptom', 'medicine_name']
        widgets = {
            'symptom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter symptom'}),
            'medicine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter medicine'}),
        }