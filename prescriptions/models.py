from django.db import models
from django.conf import settings

class Disease(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)
    disease = models.ForeignKey('Disease', on_delete=models.CASCADE)

    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.message[:40]}"
    
    
    
class ChatResponseSuggestion(models.Model):
    chat_message = models.ForeignKey(ChatMessage, related_name='suggestions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text
    
    
class SymptomMedicine(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='symptom_medicines')
    symptom = models.CharField(max_length=200)
    medicine_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.symptom} - {self.medicine_name}"
