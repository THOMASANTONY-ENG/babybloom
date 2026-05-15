from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Create your models here.
BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
    ('Unknown', 'Unknown'),
]

class Baby(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    
    weight = models.FloatField()
    height = models.FloatField()
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='Unknown', blank=True)
    
    # Twins support: babies sharing the same twins_group UUID are twins
    twins_group = models.CharField(max_length=36, blank=True, null=True, default=None)
    

    @property
    def age(self):
        from datetime import date
        today = date.today()
        diff = today - self.dob
        months = diff.days // 30
        if months == 0:
            return "Newborn"
        return f"{months} months"

    def __str__(self):
        return self.name
class GrowthLog(models.Model):
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE)
    
    weight = models.FloatField()
    height = models.FloatField()    
    
    date = models.DateField(default=timezone.now)


    def __str__(self):
        return f"{self.baby.name} - {self.date}"


NOTE_CATEGORY_CHOICES = [
    ('observation', 'Observation'),
    ('symptom', 'Symptom'),
    ('reminder', 'Reminder'),
    ('feeding', 'Feeding'),
    ('sleep', 'Sleep'),
    ('milestone', 'Milestone'),
    ('other', 'Other'),
]

class CareNote(models.Model):
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE, related_name='care_notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='care_notes')

    category = models.CharField(max_length=20, choices=NOTE_CATEGORY_CHOICES, default='observation')
    title = models.CharField(max_length=200)
    content = models.TextField()

    # Metadata flags
    is_pinned = models.BooleanField(default=False)
    share_with_doctor = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.baby.name} – {self.title}"