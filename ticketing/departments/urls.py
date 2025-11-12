from django.urls import path
from . import views

urlpatterns = [
    path('department-list/', views.department_list, name='department_list'),
    path('department-add/', views.add_department, name='add_department'),
    path('department-update/', views.update_department, name='update_department'),
    path('department-delete/<int:dept_id>/', views.delete_department, name='delete_department'),
    path("departments/check-name/", views.check_department_name, name="check_department_name"),
    #service management URLs
    path('service-list/', views.service_list, name='service_list'),
    path('service-add/', views.add_service, name='add_service'),
    path('services/delete-multiple/', views.delete_multiple_services, name='delete_multiple_services'),
    path('<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('<int:pk>/edit/', views.edit_service, name='edit_service'),
    path('check-duplicate/', views.check_service_duplicate, name='check_service_duplicate'),
    # machine kiosk URLs
    path('machine-kiosk/', views.machine_kiosk_view, name='machine_kiosk'),
    path('machine-kiosk/update/<int:comp_id>/', views.update_kiosk, name='update_kiosk'),
    path('machine-kiosk/delete/<int:comp_id>/', views.delete_kiosk, name='delete_kiosk'),


]

