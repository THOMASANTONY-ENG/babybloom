from django.urls import path
from . import api_views

urlpatterns = [
    path('api/prescriptions/', api_views.get_prescriptions, name='get_prescriptions'),
    path('api/prescriptions/add/', api_views.add_prescription, name='add_prescription_api'),
    path('api/doctor/prescriptions/', api_views.get_doctor_prescriptions, name='get_doctor_prescriptions_api'),
]

