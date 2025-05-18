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
