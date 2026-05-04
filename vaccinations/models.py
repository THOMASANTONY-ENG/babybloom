from django.db import models
from parents.models import Baby

class Vaccine(models.Model):
    name = models.CharField(max_length=100)
    recommended_age = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class VaccinationRecord(models.Model):
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE)
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.baby.name} - {self.vaccine.name}"