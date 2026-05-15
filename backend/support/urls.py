from django.urls import path

from .api_views import *

urlpatterns = [

    path(
        'api/contact/',
        create_contact_message
    ),

    path(
        'api/admin/inbox/',
        admin_inbox
    ),

    path(
        'api/admin/inbox/resolve/<int:message_id>/',
        resolve_message
    ),
]