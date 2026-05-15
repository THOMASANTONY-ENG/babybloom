from django.urls import path
from . import api_views

urlpatterns = [
    path('api/babies/', api_views.get_babies, name='get_babies'),
    path('api/babies/add/', api_views.add_baby, name='add_baby_api'),
    path('api/babies/add-twins/', api_views.add_twins, name='add_twins_api'),
    path('api/babies/<int:baby_id>/', api_views.get_baby, name='get_baby_api'),
    path('api/babies/<int:baby_id>/update/', api_views.update_baby, name='update_baby_api'),
    path('api/babies/delete/<int:baby_id>/', api_views.delete_baby, name='delete_baby_api'),
    path('api/growth/<int:baby_id>/', api_views.growth_records, name='growth_records_api'),
    path('api/growth/<int:baby_id>/add/', api_views.add_growth, name='add_growth_api'),

    # Care Notes
    path('api/babies/<int:baby_id>/notes/', api_views.get_care_notes, name='get_care_notes'),
    path('api/babies/<int:baby_id>/notes/add/', api_views.add_care_note, name='add_care_note'),
    path('api/notes/<int:note_id>/update/', api_views.update_care_note, name='update_care_note'),
    path('api/notes/<int:note_id>/delete/', api_views.delete_care_note, name='delete_care_note'),
    path('api/notes/<int:note_id>/pin/', api_views.toggle_pin_note, name='toggle_pin_note'),
    path('api/notes/<int:note_id>/share/', api_views.toggle_share_note, name='toggle_share_note'),
]
