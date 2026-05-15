from django.db import models

# Create your models here.
from django.db import models


class Resource(models.Model):

    CATEGORY_CHOICES = (

        ('vaccination', 'Vaccination'),

        ('nutrition', 'Nutrition'),

        ('development', 'Development'),

        ('emergency', 'Emergency'),
    )

    title = models.CharField(
        max_length=255
    )

    content = models.TextField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    recommended = models.BooleanField(
        default=False
    )

    def __str__(self):

        return self.title