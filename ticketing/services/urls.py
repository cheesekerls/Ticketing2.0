from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.service_list, name='service_list'),
    path('add/', views.add_service, name='add_service'),
    path('<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('<int:pk>/edit/', views.edit_service, name='edit_service'),
]
