from django.db import models
from appointments.models import Appointment

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)

    medication = models.TextField()
    dosage = models.CharField(max_length=100)
    instructions = models.TextField()

    def __str__(self):
        return f"Prescription for {self.appointment}"