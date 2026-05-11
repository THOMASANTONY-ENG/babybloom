from django.contrib import admin
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from . import views, api_views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/",views.register,name="register"),
    path("login/",views.login,name="login"),

    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('users/', views.user_list, name='user_list'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('api/test/', views.test_api),
    path('api/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('api/admin/dashboard/', api_views.admin_dashboard_api),
    path('api/me/',api_views.get_user_profile),
    path('api/register/', api_views.register_api, name='api_register'),
    path('api/admin/doctors/', api_views.manage_doctors_api, name='api_manage_doctors'),
    path('api/admin/doctors/<int:doc_id>/', api_views.modify_doctor_api, name='api_modify_doctor'),
    path('api/notifications/', api_views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notif_id>/read/', api_views.mark_notification_read, name='mark_notification_read'),
]



