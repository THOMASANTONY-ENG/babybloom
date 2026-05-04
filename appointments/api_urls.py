from django.urls import path
from . import api_views

urlpatterns = [
    path('api/appointments/', api_views.get_parent_appointments, name='get_parent_appointments'),
    path('api/appointments/book/', api_views.book_appointment, name='book_appointment_api'),
    path('api/doctor/appointments/', api_views.get_doctor_appointments, name='get_doctor_appointments_api'),
    path('api/appointments/update/<int:appointment_id>/', api_views.update_appointment_status, name='update_appointment_status_api'),
]

