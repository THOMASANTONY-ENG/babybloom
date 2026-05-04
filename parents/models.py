from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Baby(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    
    weight = models.FloatField()
    height = models.FloatField()
    

    def __str__(self):
        return self.name
class GrowthLog(models.Model):
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE)
    
    weight = models.FloatField()
    height = models.FloatField()    
    
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.baby.name} - {self.date}"