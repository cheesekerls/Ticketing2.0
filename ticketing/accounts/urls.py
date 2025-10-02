from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name="accounts/templates/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    # Dashboards
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
