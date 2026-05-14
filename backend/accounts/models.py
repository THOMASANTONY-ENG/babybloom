from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES = (
        ('parent','Parent'),
        ('doctor','Doctor'),
        ('admin','Admin'),
    )
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    role = models.CharField(max_length = 10,choices = ROLE_CHOICES)

    def __str__(self):
        return self.user.username

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}..."
