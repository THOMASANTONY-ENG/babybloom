from django.urls import path
from . import api_views

urlpatterns = [
    path('api/appointments/', api_views.get_parent_appointments, name='get_parent_appointments'),
    path('api/appointments/book/', api_views.book_appointment, name='book_appointment_api'),
    path('api/doctor/appointments/', api_views.get_doctor_appointments, name='get_doctor_appointments_api'),
    path('api/doctor/dashboard/', api_views.get_doctor_dashboard, name='get_doctor_dashboard_api'),
    path('api/appointments/update/<int:appointment_id>/', api_views.update_appointment_status, name='update_appointment_status_api'),
    path('api/patient-history/<int:baby_id>/', api_views.patient_history, name='patient_history_api'),
    path('api/appointments/create-availability/', api_views.create_availability, name='create_availability_api'),
    path('api/appointments/available-slots/<int:doctor_id>/', api_views.available_slots, name='available_slots_api'),
    path('api/appointments/bulk-availability/', api_views.bulk_create_availability, name='bulk_availability_api'),
    path('api/doctor/upcoming-slots/', api_views.get_upcoming_slots, name='get_upcoming_slots_api'),
    path('api/doctor/availability/delete/<int:slot_id>/', api_views.delete_availability, name='delete_availability_api'),
    path('api/doctor/availability/bulk-delete/', api_views.bulk_delete_availability, name='bulk_delete_availability_api'),
]

