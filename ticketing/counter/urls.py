from django.urls import path
from . import views

urlpatterns = [
    path('', views.queue_dashboard, name='queue_dashboard'),
    path('call-next/', views.call_next_ticket, name='call_next_ticket'),
    path('skip/<str:ticket_number>/', views.skip_ticket, name='skip_ticket'),
    path('counter/cancel/<str:ticket_number>/', views.cancel_ticket, name='cancel_ticket'),
]
