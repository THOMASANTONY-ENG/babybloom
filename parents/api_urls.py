from django.urls import path
from . import api_views

urlpatterns = [
    path('api/babies/', api_views.get_babies, name='get_babies'),
    path('api/babies/add/', api_views.add_baby, name='add_baby_api'),
    path('api/babies/delete/<int:baby_id>/', api_views.delete_baby, name='delete_baby_api'),
    path('api/growth/<int:baby_id>/', api_views.growth_records, name='growth_records_api'),
    path('api/growth/<int:baby_id>/add/', api_views.add_growth, name='add_growth_api'),
]
