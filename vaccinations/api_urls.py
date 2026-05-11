from django.urls import path
from . import api_views

urlpatterns = [
    path('api/vaccine-reminders/<int:baby_id>/', api_views.vaccine_reminders, name='vaccine_reminders_api'),
]
