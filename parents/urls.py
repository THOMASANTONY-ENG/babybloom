from django.urls import path
from . import views, api_views

urlpatterns = [
    path('add/', views.add_baby, name='add_baby'),
    path('', views.view_babies, name='view_babies'),
    path('edit/<int:baby_id>/',views.edit_baby, name='edit_baby'),
    path('delete/<int:baby_id>/',views.delete_baby, name='delete_baby'),
    path('growth/add/<int:baby_id>/', views.add_growth, name='add_growth'),
    path('growth/<int:baby_id>/', views.view_growth, name='view_growth'),

    path('growth/<int:baby_id>/', views.view_growth, name='view_growth'),
]
