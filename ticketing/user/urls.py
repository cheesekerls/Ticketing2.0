from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('scan/', views.scan_qrcode, name='scan_qrcode'),
    path('ticket/<str:ticket_number>/', views.queue_status, name='queue_status'),
    path('queue-status/', views.queue_status_redirect, name='queue_status_redirect'),
    path('user/cancel-ticket/<str:ticket_number>/', views.cancel_ticket, name='cancel_ticket'),

]
