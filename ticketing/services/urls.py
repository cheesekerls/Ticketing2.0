from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.service_list, name='service_list'),
    path('add/', views.add_service, name='add_service'),
    path('services/delete-multiple/', views.delete_multiple_services, name='delete_multiple_services'),
    path('<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('<int:pk>/edit/', views.edit_service, name='edit_service'),
<<<<<<< HEAD
    path('check-duplicate/', views.check_service_duplicate, name='check_service_duplicate'),

]
=======
]
>>>>>>> 7f3ae303ec1a32272dd33bb3630375691e77c039
