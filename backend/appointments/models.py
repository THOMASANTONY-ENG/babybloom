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
    time = models.TimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

class DoctorAvailability(models.Model):

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_booked = models.BooleanField(
        default=False
    )

    def __str__(self):

        return (
            f"{self.doctor.user.username}"
            f" - {self.date}"
        )