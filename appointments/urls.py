from django.urls import path
from . import views
from .views import book_appointment, view_appointments, update_appointment
from django.urls import path

from . import api_views

urlpatterns = [
    path('', view_appointments, name='view_appointments'),
    path('book/', book_appointment, name='book_appointment'),
    path("update/<int:appointment_id>/", update_appointment, name="update_appointment"),
    path("doctor/", views.doctor_appointments, name="doctor_appointments"),
    path('api/prescriptions/add/', api_views.create_prescription, name='create_prescription'),
]