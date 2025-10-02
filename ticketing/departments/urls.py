from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_list, name='department_list'),
    path('add/departments/', views.add_department, name='add_department'),
]
