from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='timetrack/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/<int:entry_id>/', views.clock_out, name='clock_out'),
    path('time-entry/create/', views.time_entry_create, name='time_entry_create'),
    path('time-entry/<int:entry_id>/edit/', views.time_entry_edit, name='time_entry_edit'),
    path('time-entry/<int:entry_id>/delete/', views.time_entry_delete, name='time_entry_delete'),
    # Admin views
    path('admin-dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('pay-report/', admin_views.pay_report, name='pay_report'),
]