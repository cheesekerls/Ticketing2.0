from django.urls import path
from . import views

urlpatterns = [
    # ✅ Ticket creation + printing (main entry point)
    path('print/<int:service_id>/', views.print_ticket_to_pos, name='print_ticket_to_pos'),
    path('print/', views.print_ticket_to_pos, name='print_ticket_no_service'),

]