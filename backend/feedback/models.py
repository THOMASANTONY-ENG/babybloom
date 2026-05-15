from django.db import models

# Create your models here.
from django.db import models

from django.contrib.auth.models import User


class Feedback(models.Model):

    FEEDBACK_TYPES = (

        ('private', 'Private'),

        ('testimonial', 'Testimonial'),
    )

    CATEGORY_CHOICES = (

        ('doctor', 'Doctor'),

        ('platform', 'Platform'),

        ('clinic', 'Clinic'),

        ('suggestion', 'Suggestion'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        default='private'
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    message = models.TextField()

    rating = models.IntegerField(
        default=5
    )

    approved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.user.username}"
            f" - {self.feedback_type}"
        )