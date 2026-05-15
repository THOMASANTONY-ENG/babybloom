from django.urls import path
from . import api_views, test_views

urlpatterns = [
    path('api/send-reminders/', api_views.send_all_reminders, name='send_all_reminders_api'),
    path('api/test-email/', test_views.test_email_config, name='test_email_config'),
]