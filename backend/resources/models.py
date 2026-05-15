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

    image_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional URL for an image cover"
    )

    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional YouTube or Video URL"
    )

    external_link = models.URLField(
        blank=True,
        null=True,
        help_text="Optional link to an external article or source"
    )

    def __str__(self):

        return self.title