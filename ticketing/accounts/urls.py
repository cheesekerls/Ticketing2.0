from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.universal_login, name='login'),
    path("logout/", views.custom_logout, name="logout"),
    path("employees/", views.admin_list, name="admin_list"),
    path('edit_employee/', views.edit_employee, name='edit_employee'),
    path('employees/delete/<int:emp_id>/', views.delete_employee, name='delete_employee'),
    path('moderator/dashboard/', views.moderator_dashboard, name='moderator_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('add_admin/', views.add_admin, name='add_admin'),  
    path('set-password/<token>/', views.set_password, name='set_password'),  # ✅ correct
    path('forbidden/', views.forbidden_view, name='forbidden'),
    path('employee/list/', views.employee_list, name='employee_list'),
    path('reports/', views.reports, name='reports'),
    path('change-password/', views.admin_change_password, name='change_password'),


]
