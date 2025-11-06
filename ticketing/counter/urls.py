from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.counter_list, name='counter_list'),
    path('add/', views.add_counter, name='add_counter'),
    path('counter_dashboard/', views.counter_dashboard, name='counter_dashboard'),
    path('call_next_ticket/', views.call_next_ticket, name='call_next_ticket'),
    path('skip_ticket/<str:ticket_number>/', views.skip_ticket, name='skip_ticket'),
    path('cancel_ticket/<str:ticket_number>/', views.cancel_ticket, name='cancel_ticket'),
    path('counter/edit/<int:counter_id>/', views.edit_counter, name='edit_counter'),
    path('counter/delete/<int:counter_id>/', views.delete_counter, name='delete_counter'),
    path('back_to_queue/<str:ticket_number>/', views.back_to_queue, name='back_to_queue'),
    path('counters/delete/<int:counter_id>/', views.delete_counter, name='delete_counter')

]