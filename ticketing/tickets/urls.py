from django.urls import path
from . import views

urlpatterns = [
    # ✅ Ticket creation + printing (main entry point)
    path('print/<int:service_id>/', views.print_ticket_to_pos, name='print_ticket_to_pos'),
    path('print/', views.print_ticket_to_pos, name='print_ticket_no_service'),

    # ✅ Queue management
    path('queue/', views.manage_queue, name='manage_queue'),
    path('service/<int:service_id>/actions/', views.service_actions, name='service_actions'),

    # ✅ Ticket actions
    path('<int:ticket_id>/served/', views.mark_served, name='mark_served'),
    path('<int:ticket_id>/skip/', views.skip_ticket, name='skip_ticket'),
    path('<int:ticket_id>/serve_skipped/', views.serve_skipped, name='serve_skipped'),
    path('<int:ticket_id>/missed/', views.mark_missed, name='mark_missed'),
    path('<int:ticket_id>/end/', views.end_session, name='end_session'),

    # ✅ Other pages
    path('history/', views.history_view, name='history'),
    path('scan/', views.scan_qrcode, name='scan_qrcode'),

    # ✅ Ticket details (placed last)
    path('<str:ticket_number>/detail/', views.ticket_detail, name='ticket_detail'),
    path('<str:ticket_number>/', views.queue_status, name='queue_status'),
]
