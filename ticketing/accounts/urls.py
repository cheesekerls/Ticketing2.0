from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path("logout/", views.custom_logout, name="logout"),
    path('superadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("employees/", views.employee_list, name="employee_list"),
    path('employees/update/', views.update_employee, name='update_employee'),
    path('employees/delete/<int:emp_id>/', views.delete_employee, name='delete_employee'),
    path('add_admin/', views.add_admin, name='add_admin'),
    
]
