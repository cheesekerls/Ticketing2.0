from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    # Main ticket creation (without service_id)
    path('print/', views.print_ticket_to_pos, name='print_ticket_no_service'),
    
    # Kiosk landing page (service selection)
    path('kiosk/', views.kiosk_home, name='kiosk_home'),
    
    # Print ticket for a specific service
    path('kiosk/ticket/<int:service_id>/', views.print_ticket_to_pos, name='print_ticket_to_pos'),
    
    # Queue & ticket management
    path('queue/<str:ticket_number>/', views.queue_status, name='queue_status'),
    path('ticket/<str:ticket_number>/', views.ticket_detail, name='ticket_detail'),
    path('manage/', views.manage_queue, name='manage_queue'),
    path('history/', views.history_view, name='history_view'),
]
