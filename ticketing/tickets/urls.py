from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    # Main ticket creation (without service_id)
    # path('kiosk/', views.kiosk_home, name='kiosk_home'),
    path('print_ticket_to_pos/<int:service_id>/', views.print_ticket_to_pos, name='print_ticket_to_pos'),
]
