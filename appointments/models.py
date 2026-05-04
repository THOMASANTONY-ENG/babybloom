from django.db import models
from parents.models import Baby
from doctors.models import Doctor

# Create your models here.
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled','Scheduled'),
        ('completed','Completed'),
        ('cancelled','Cancelled')
    )
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length = 10, choices = STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"{self.baby.name} - {self.doctor}"