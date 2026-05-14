from django.urls import path
from . import api_views

urlpatterns = [
    path('api/doctors/', api_views.get_doctors_api, name='get_doctors_api'),
]
