from django.urls import path
from .import views

urlpatterns = [
    path('add/<int:appointment_id>/', views.add_prescription, name='add_prescription'),
    path('view/<int:appointment_id>/', views.view_prescription, name='view_prescription'),
    path('', views.view_prescriptions, name='view_prescriptions'),
]