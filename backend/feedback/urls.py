from django.urls import path

from .api_views import *

urlpatterns = [

    path(
        'api/feedback/create/',
        create_feedback
    ),

    path(
        'api/feedback/private/',
        private_feedbacks
    ),

    path(
        'api/testimonials/',
        approved_testimonials
    ),

    path(
        'api/feedback/all/',
        all_feedbacks
    ),
    path(
        'api/testimonials/approve/<int:feedback_id>/',
        approve_testimonial
    ),
]