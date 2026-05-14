from django.db import models
from appointments.models import Appointment

class Prescription(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE
    )

    diagnosis = models.TextField(
        null=True,
        blank=True
    )

    medicines = models.TextField()

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True          
    )
    
    def __str__(self):
        return self.appointment.baby.name