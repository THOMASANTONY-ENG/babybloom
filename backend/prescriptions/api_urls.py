from django.urls import path
from . import api_views

urlpatterns = [
    path('api/prescriptions/', api_views.get_prescriptions, name='get_prescriptions'),
    path('api/prescriptions/add/', api_views.add_prescription, name='add_prescription_api'),
    path('api/doctor/prescriptions/', api_views.get_doctor_prescriptions, name='get_doctor_prescriptions_api'),
    path('api/prescriptions/<int:appointment_id>/', api_views.get_prescription_by_appointment, name='get_prescription_by_appointment'),
    path('api/prescriptions/edit/<int:pk>/', api_views.edit_prescription, name='edit_prescription_api'),
]

