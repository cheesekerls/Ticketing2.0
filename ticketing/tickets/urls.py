from django.urls import path
from . import views


urlpatterns = [
    path('print/<int:service_id>/', views.print_ticket_to_pos, name='print_ticket_to_pos'),
    path('print/', views.print_ticket_to_pos, name='print_ticket_no_service'),

    path('queue/<str:ticket_number>/', views.queue_status, name='queue_status'),
    path('ticket/<str:ticket_number>/', views.ticket_detail, name='ticket_detail'),
    path('manage/', views.manage_queue, name='manage_queue'),
    path('history/', views.history_view, name='history_view'),
]