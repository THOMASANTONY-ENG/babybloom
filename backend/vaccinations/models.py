from django.db import models
from parents.models import Baby
from django.contrib.auth.models import User

class Vaccine(models.Model):
    name = models.CharField(max_length=100)
    recommended_age = models.CharField(max_length=50)

    def __str__(self):
        return self.name

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('overdue', 'Overdue'),
)

class VaccinationRecord(models.Model):
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE)
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.baby.name} - {self.vaccine.name}"

class VaccineSchedule(models.Model):
    name = models.CharField(max_length=100)
    due_days = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.due_days} days)"

class BabyVaccine(models.Model):
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE)
    vaccine = models.ForeignKey(VaccineSchedule, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_given = models.DateField(null=True, blank=True)
    
    # Professional fields
    batch_number = models.CharField(max_length=50, null=True, blank=True)
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.baby.name} - {self.vaccine.name}"