from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Doctor(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)

    speciality = models.CharField(max_length=100)
    experience = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Dr {self.user.username}"