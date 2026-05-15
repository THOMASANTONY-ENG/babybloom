from django.urls import path

from .api_views import *

urlpatterns = [

    path(
        'api/resources/',
        resources_list
    ),

    path(
        'api/resources/create/',
        create_resource
    ),

    path(
        'api/resources/recommended/',
        recommended_resources
    ),
]