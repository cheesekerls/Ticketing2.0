from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import JsonResponse
from accounts.models import Employee
from services.models import Service
from tickets.models import Ticket
from .models import Counter
from accounts.decorators import role_required, department_admin_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import secrets


# ---------------------- ADMIN VIEWS ----------------------

@role_required('Admin')
@department_admin_required
def counter_list(request):
    """List all counters under the admin's department."""
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, pk=employee_id)
    dept = employee.department
    all_services = Service.objects.filter(department=dept)  # ✅ Fetch services for the department

    counters = Counter.objects.filter(department=dept)
    return render(request, 'counter_list.html', {
        'counters': counters,
        'department_name': dept.department_name,
        "all_services": all_services,  # ✅ Pass to template

    })



@role_required('Admin')
@department_admin_required
def add_counter(request):
    """Add a new counter, assign services, and send password setup link (Admin-style)."""
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, pk=employee_id)
    dept = employee.department
    available_services = Service.objects.filter(department=dept)

    if request.method == 'POST':
        email = request.POST.get('email')
        counter_number = request.POST.get('counter_number')
        selected_services = request.POST.getlist('services')

        # ✅ Prevent duplicates
        if Counter.objects.filter(email=email).exists() or Employee.objects.filter(email=email).exists():
            messages.error(request, "⚠️ A user with this email already exists.")
            return redirect('counter_list')

        # ✅ Create Employee entry for authentication
        employee_account = Employee.objects.create(
            email=email,
            department=dept,
            position="Counter",
            password="",  # No password until they set it
            is_active=True,
        )

        # ✅ Create Counter record linked to Employee
        counter = Counter.objects.create(
            email=email,
            counter_number=counter_number,
            department=dept,
        )
        counter.services.set(selected_services)

        # ✅ Generate a unique secure token for password setup
        token = secrets.token_urlsafe(32)
        employee_account.password_reset_token = token
        employee_account.save()

        # ✅ Build password setup link
        reset_link = request.build_absolute_uri(
            reverse('set_password', kwargs={'token': token})
        )

        # ✅ Send invitation email (HTML)
        subject = "Set Your Password - Counter Account"
        html_content = f"""
            <p>Hello,</p>
            <p>You’ve been added as a <strong>Counter</strong> in the <strong>{dept.department_name}</strong> Department.</p>
            <p>Please click the link below to set your password and activate your account:</p>
            <p><a href="{reset_link}">Set Password</a></p>
            <p>If you did not expect this email, you can ignore it.</p>
        """
        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, f"✅ Counter added successfully. Password setup link sent to {email}.")
        return redirect('counter_list')

    return render(request, 'add_counter.html', {
        'services': available_services,
        'department_name': dept.department_name,
    })

# ---------------------- COUNTER DASHBOARD ----------------------
@role_required('Counter')
def counter_dashboard(request):
    """
    Counter dashboard: show only tickets belonging to assigned services.
    """
    email = request.session.get('email')
    if not email:
        return redirect('login')

    counter = get_object_or_404(Counter, email=email)
    assigned_services = counter.services.all()

    # ✅ Show only tickets belonging to the counter's assigned services
    for idx, t in enumerate(
        Ticket.objects.filter(service__in=assigned_services, status__in=['Waiting', 'Skipped']).order_by('created_at'),
        start=1
    ):
        if not t.queue_position:
            t.queue_position = idx
            t.save()

    tickets = Ticket.objects.filter(service__in=assigned_services, status__in=['Waiting', 'Skipped']).order_by('queue_position')
    current_ticket = Ticket.objects.filter(service__in=assigned_services, status='Called').last()

    return render(request, 'counter_dashboard.html', {
        'tickets': tickets,
        'current_ticket': current_ticket,
        'assigned_services': assigned_services,
        'counter_number': counter.counter_number,
    })


# ---------------------- QUEUE ACTIONS ----------------------

@transaction.atomic
def call_next_ticket(request):
    """Call next ticket only from assigned services."""
    email = request.session.get('email')
    counter = get_object_or_404(Counter, email=email)
    assigned_services = counter.services.all()

    Ticket.objects.filter(service__in=assigned_services, status='Called').update(status='Served')

    next_ticket = (
        Ticket.objects.filter(service__in=assigned_services, status='Waiting')
        .order_by('queue_position', 'created_at', 'ticket_id')
        .select_for_update(skip_locked=True)
        .first()
    )

    if next_ticket:
        next_ticket.status = 'Called'
        next_ticket.save()

    return redirect('queue_dashboard')


def skip_ticket(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    next_ticket = Ticket.objects.filter(
        queue_position__gt=ticket.queue_position,
        status__in=['Waiting', 'Skipped']
    ).order_by('queue_position').first()

    if next_ticket:
        ticket.queue_position, next_ticket.queue_position = next_ticket.queue_position, ticket.queue_position
        ticket.status = 'Skipped'
        ticket.save()
        next_ticket.save()
    else:
        ticket.status = 'Skipped'
        ticket.save()

    return redirect('queue_dashboard')


def cancel_ticket(request, ticket_number):
    if request.method == 'POST':
        try:
            ticket = Ticket.objects.get(ticket_number=ticket_number)
            ticket.status = 'Cancelled'
            ticket.save()
            return JsonResponse({'success': True})
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Counter

def edit_counter(request, counter_id):
    counter = get_object_or_404(Counter, pk=counter_id)

    if request.method == "POST":
        counter.counter_number = request.POST.get("counter_number")
        service_ids = request.POST.getlist("services")

        # ✅ Save Counter first (for M2M)
        counter.save()

        # ✅ Update many-to-many relationship
        counter.services.set(service_ids)

        messages.success(request, f"Counter '{counter.email}' updated successfully.")
        return redirect("counter_list")  # change to your actual template view name

    # Optional if you want to handle GET (not needed with modal)
    return redirect("counter_list")


def delete_counter(request, counter_id):
    counter = get_object_or_404(Counter, pk=counter_id)
    if request.method == "POST":
        counter.delete()
        return redirect("counter_list")
    return redirect("counter_list")



def back_to_queue(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    ticket.status = "Waiting"
    ticket.save()
    return redirect('queue_dashboard')