from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path("logout/", views.custom_logout, name="logout"),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("employees/", views.employee_list, name="employee_list"),
    path('add_staff/', views.add_staff, name='add_staff'),
    
]
