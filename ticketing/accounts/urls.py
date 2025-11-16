from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.universal_login, name='login'),
    path("logout/", views.custom_logout, name="logout"),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    #admin
    path("Moderator-list/", views.moderator_list, name="moderator_list"),
    path('edit_employee/', views.edit_moderator, name='edit_moderator'),
    path('employees/delete/<int:emp_id>/', views.delete_moderator, name='delete_moderator'),
    path('moderator-dashboard/', views.moderator_dashboard, name='moderator_dashboard'),
    path('add_moderator/', views.add_moderator, name='add_moderator'),  
    path('set-password/<token>/', views.set_password, name='set_password'),  # ✅ correct
    path('forbidden/', views.forbidden_view, name='forbidden'),
    path('reports/', views.report_dashboard, name='report_dashboard'),
    path('change-password/', views.moderator_change_password, name='change_password'),
    #counter
    path('counter-list/', views.counter_list, name='counter_list'),
    path('add/', views.add_counter, name='add_counter'),
    path('queue_dashboard/', views.counter_dashboard, name='counter_dashboard'),
    path('queue_dashboard/back/<str:ticket_number>/', views.back_to_queue, name='back_to_queue'),
    path('call_next_ticket/', views.call_next_ticket, name='call_next_ticket'),
    path('queue_dashboard/skip_current/<str:ticket_number>/', views.skip_ticket, name='skip_ticket'),
    path('cancel_ticket/<str:ticket_number>/', views.cancel_ticket, name='cancel_ticket'),
    path('counter/edit/<int:counter_id>/', views.edit_counter, name='edit_counter'),
    path('counter/delete/<int:counter_id>/', views.delete_counter, name='delete_counter'),
    path('counter/set-password/<str:token>/', views.setpassword_counter, name='setpassword_counter'),
    path('counter/services_dashboard/', views.services_dashboard, name='services_dashboard'),

    # path('machine-kiosk/add/', views.service_dashboard, name='add_kiosk'),
    #RESET PASSWORD
    path('forgot-password/', views.password_reset_request, name='password_reset'),
    path('reset-password/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('display/', views.ticket_display, name='ticket_display'),
    path('api/tickets/', views.tickets_api, name='tickets_api'),

]
