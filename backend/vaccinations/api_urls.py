from django.urls import path
from . import api_views

urlpatterns = [
    path('api/vaccine-reminders/<int:baby_id>/', api_views.vaccine_reminders, name='vaccine_reminders_api'),
    path('api/vaccine-milestones/<int:baby_id>/', api_views.vaccine_milestone_timeline, name='vaccine_milestone_timeline'),
    path('api/vaccine-reminders/all/', api_views.all_vaccination_reminders, name='all_vaccine_reminders_api'),
    path('api/vaccinations/schedules/', api_views.manage_vaccine_schedules, name='manage_vaccine_schedules'),
    path('api/vaccinations/schedules/<int:pk>/', api_views.modify_vaccine_schedule, name='modify_vaccine_schedule'),
    path('api/vaccinations/update-record/<int:record_id>/', api_views.update_baby_vaccine, name='update_baby_vaccine'),
]
