from django.db import models
from parents.models import Baby
from doctors.models import Doctor
from django.contrib.auth.models import User

# Create your models here.

class Appointment(models.Model):
    STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('completed', 'Completed'),
)


    parent = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    baby = models.ForeignKey(Baby, on_delete=models.CASCADE)

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )