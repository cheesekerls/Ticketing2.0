from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.service_list, name='service_list'),
    path('add/', views.add_service, name='add_service'),
    path('services/delete-multiple/', views.delete_multiple_services, name='delete_multiple_services'),
    path('<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('<int:pk>/edit/', views.edit_service, name='edit_service'),
    path('check-duplicate/', views.check_service_duplicate, name='check_service_duplicate'),
    path('machine-kiosk/', views.machine_kiosk_view, name='machine_kiosk'),
    path('machine-kiosk/update/<int:comp_id>/', views.update_kiosk, name='update_kiosk'),
    path('machine-kiosk/delete/<int:pk>/', views.delete_kiosk, name='delete_kiosk'),

]
