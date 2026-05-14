from django.urls import path
from . import views

urlpatterns = [
    path("baby/<int:baby_id>/", views.vaccination_list, name="vaccination_list"),
    path("mark/<int:baby_id>/<int:vaccine_id>/", views.mark_vaccine, name="mark_vaccine"),
    path('', views.vaccine_list, name='vaccine_list'),
    path('add/', views.add_vaccine, name='add_vaccine'),
    path('delete/<int:vaccine_id>/', views.delete_vaccine, name='delete_vaccine'),
]
