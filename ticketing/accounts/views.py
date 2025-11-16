import sys
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from .forms import AdminInviteForm
from .models import Employee, UserProfile
from departments.models import Department
from django.core.mail import EmailMultiAlternatives, get_connection
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User  # or your CustomUser model
from django.contrib.auth.hashers import make_password
from accounts.decorators import department_moderator_required, role_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout
import secrets
from accounts.models import Employee as StaffEmployee  # rename to avoid clash
from .forms import ChangePasswordForm
from accounts.models import Employee  # or your Admin user model
from departments.models import Service
from .models import Counter
from tickets.models import Ticket
from datetime import date
import json
from django.db.models import Count
from django.http import HttpResponse
import csv
from django.utils.timezone import now
from django.http import JsonResponse
from django.db import transaction
from django.utils.crypto import get_random_string
import urllib.parse
from django.http import JsonResponse


User = get_user_model()


def universal_login(request):
    if request.method == "POST":
        identifier = request.POST.get("email")  # can be email OR username
        password = request.POST.get("password")

        # ========== 1️⃣ DJANGO USER (Admin / Moderator via UserProfile) ==========
        user = None
        try:
            if "@" in identifier:
                user_obj = User.objects.filter(email=identifier).first()
            else:
                user_obj = User.objects.filter(username=identifier).first()

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
        except Exception:
            user = None

        if user is not None:
            login(request, user)
            request.session["email"] = user.email
            return redirect("admin_dashboard")

        # ========== 2️⃣ EMPLOYEE (Moderator / Staff) ==========
        employee = None
        try:
            if "@" in identifier:
                employee = Employee.objects.filter(email=identifier).first()
            else:
                employee = Employee.objects.filter(username=identifier).first() if hasattr(Employee, "username") else None
        except Exception:
            employee = None

        if employee and check_password(password, employee.password):
            request.session["employee_id"] = employee.employee_id
            request.session["employee_position"] = employee.position
            request.session["employee_department"] = (
                employee.department.department_id if employee.department else None
            )
            request.session["email"] = employee.email

            if employee.position.lower() == "moderator":
                return redirect("moderator_dashboard")
            else:
                messages.error(request, "No dashboard assigned for this role.")
                return render(request, "login.html")

        # ========== 3️⃣ COUNTER (Queue Counter Users) ==========
        counter = None
        try:
            if "@" in identifier:
                counter = Counter.objects.filter(email=identifier).first()
        except Exception:
            counter = None

        if counter:
            if check_password(password, counter.password) or counter.password == password:
                # ✅ Save counter_id for decorators & sessions
                request.session["counter_id"] = counter.counter_id
                request.session["email"] = counter.email
                messages.success(request, f"Welcome, Counter {counter.counter_number}!")

                # ✅ Redirect Counter #0 → services_dashboard; others → counter_dashboard
                if str(counter.counter_number) == "0":
                    return redirect("services_dashboard")
                else:
                    return redirect("counter_dashboard")

        # ========== ❌ NO MATCH ==========
        messages.error(request, "Invalid username/email or password.")
        return render(request, "login.html")

    return render(request, "login.html")


def custom_logout(request):
    logout(request)
    request.session.flush()
    return redirect("login")
@role_required(["Admin"])
def admin_dashboard(request):
    total_departments = Department.objects.count()
    total_moderators = Employee.objects.filter(position='Moderator').count()  # assuming position='admin'

    # For chart
    departments = Department.objects.all()
    department_labels = [dept.department_name for dept in departments]
    moderators_counts = [Employee.objects.filter(position='Moderator', department=dept).count() for dept in departments]

    # Get all moderators for table
    moderators = Employee.objects.filter(position='Moderator').select_related('department')

    context = {
        'total_departments': total_departments,
        'total_moderators': total_moderators,
        'department_labels': department_labels,
        'moderators_counts': moderators_counts,
        'moderators': moderators
    }

    return render(request, 'admin_dashboard.html', context)

@role_required('Moderator')
def moderator_dashboard(request):
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(Employee, pk=employee_id)

    # ✅ Only count services belonging to this admin's department
    total_services = Service.objects.filter(department=employee.department).count()
    total_users = Counter.objects.filter(department=employee.department).count()

    context = {
        'total_services': total_services,
        'total_users': total_users,
    }
    return render(request, 'moderator/moderator_dashboard.html', context)



@department_moderator_required
def department_dashboard(request, department_id):
    employee = Employee.objects.get(email=request.session.get("email"))
    return render(request, 'moderator_dashboard.html', {"employee": employee})

@role_required("Admin")
def moderator_list(request):
    employees = Employee.objects.all()
    return render(request, "moderator/moderator_list.html", {"employees": employees})


def forbidden_view(request):
    return render(request, '403.html', status=403)


def edit_moderator(request):
    if request.method == 'POST':
        emp_id = request.POST.get('id')
        employee = get_object_or_404(Employee, pk=emp_id)
        employee.name = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.department = request.POST.get('department_name')
        messages.success(request, "Employee updated successfully!")
        employee.save()

    return redirect('moderator_list')

def moderator_change_password(request):
    user_id = request.session.get('employee_id')  # your custom moderator session
    if not user_id:
        return redirect('login')

    user = Employee.objects.get(pk=user_id)

    if request.method == "POST":
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, "Password updated successfully!")
            return redirect('moderator_dashboard')
    else:
        form = ChangePasswordForm(user)

    return render(request, 'moderator/change_password.html', {'form': form})


def delete_moderator(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    return redirect('moderator_list')



def reports(request):
    return render(request, 'reports.html')


@login_required
@role_required('Admin')
def add_moderator(request):
    if request.method == 'POST':
        form = AdminInviteForm(request.POST)
    else:
        form = AdminInviteForm()

    departments_with_admin = Employee.objects.filter(position='Moderator').values_list('department_id', flat=True)

    # ✅ Only show departments that do NOT have an Admin yet
    form.fields['department'].queryset = Department.objects.exclude(department_id__in=departments_with_admin)

    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        department = form.cleaned_data['department']       

        # ✅ Create Admin in Employee table only
        employee = Employee.objects.create(
            name=name,
            email=email,
            department=department,
            position="Moderator",
            password="",  # Empty for now until password is set
            is_active=True,
        )

        # ✅ Generate secure password setup link
        token = secrets.token_urlsafe(32)
        employee.password_reset_token = token
        employee.save()

        reset_link = request.build_absolute_uri(
            reverse('set_password', kwargs={'token': token})
        )

        # ✅ Send email invitation
        subject = "Set your Moderator account password"
        html_content = f"""
            <p>Hello {name},</p>
            <p>You have been added as a Moderator in <strong>{department.department_name}</strong>.</p>
            <p>Click the link below to set your password and activate your account:</p>
            <p><a href="{reset_link}">Set Password</a></p>
            <p>If you did not expect this email, you can ignore it.</p>
        """
        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, f"Moderator '{name}' invited! A password setup email has been sent.")
        return redirect('moderator_list')

    return render(request, 'moderator/add_moderator_department.html', {'form': form})


def set_password(request, token):
    employee = get_object_or_404(Employee, password_reset_token=token)

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path)

        employee.set_password(password)
        employee.password_reset_token = None
        employee.save()

        messages.success(request, "Password set successfully! You can now log in.")
        return redirect('login')

    return render(request, 'moderator/set_password.html', {'employee': employee})

@role_required('Moderator')
def report_dashboard(request):
    # ✅ Check if employee is logged in
    employee_id = request.session.get('employee_id')
    
    if not employee_id:
        messages.warning(request, 'Please login first.')
        return redirect('universal_login')
    
    # ✅ Get employee and department
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        department = employee.department
    except Employee.DoesNotExist:
        messages.error(request, 'Employee not found. Please login again.')
        return redirect('universal_login')
    
    # ✅ Check if employee has department
    if not department:
        messages.warning(request, 'You are not assigned to any department.')
        context = {
            'today_tickets': 0,
            'monthly_tickets': 0,
            'yearly_tickets': 0,
            'total_tickets': 0,
            'service_summary': [],
            'monthly_data': [],
            'department': None,
            'employee': employee,
        }
        return render(request, 'moderator/moderator_reports.html', context)
    
    # ✅ Date calculations
    today = now().date()
    month = today.month
    year = today.year
    
    print("=" * 50)
    print(f"👤 Employee: {employee.name}")
    print(f"🏢 Department: {department.department_name}")
    print(f"🆔 Department ID: {department.department_id}")
    print("=" * 50)
    
    # ✅ FIX: filter by department through service
    tickets = Ticket.objects.filter(service__department=department)
    
    print(f"📊 Total tickets for {department.department_name}: {tickets.count()}")
    
    # ✅ Count tickets (daily, monthly, yearly)
    today_tickets = tickets.filter(created_at__date=today).count()
    monthly_tickets = tickets.filter(created_at__year=year, created_at__month=month).count()
    yearly_tickets = tickets.filter(created_at__year=year).count()
    total_tickets = tickets.count()
    
    # ✅ Ticket count per service (for this department only)
    service_summary = (
        tickets.values('service__service_name')
        .annotate(total=Count('ticket_id'))
        .order_by('-total')
    )
    
    # ✅ Monthly chart data (for this department only)
    monthly_data = (
        tickets.filter(created_at__year=year)
        .values('created_at__month')
        .annotate(total=Count('ticket_id'))
        .order_by('created_at__month')
    )
    
    context = {
        'today_tickets': today_tickets,
        'monthly_tickets': monthly_tickets,
        'yearly_tickets': yearly_tickets,
        'total_tickets': total_tickets,
        'service_summary': service_summary,
        'monthly_data': monthly_data,
        'department': department,
        'employee': employee,
    }

    return render(request, 'moderator/moderator_reports.html', context)




# ---------------------- MODERATOR VIEWS ----------------------

@role_required('Moderator')
def counter_list(request):
    """List all counters under the admin's department."""
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, pk=employee_id)
    dept = employee.department
    all_services = Service.objects.filter(department=dept)  # ✅ Fetch services for the department

    counters = Counter.objects.filter(department=dept)
    return render(request, 'counter/counter_list.html', {
        'counters': counters,
        'department_name': dept.department_name,
        "all_services": all_services,  # ✅ Pass to template

    })


@role_required('Moderator')
def add_counter(request):
    """Moderator invites a new counter and assigns multiple services."""
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, pk=employee_id)
    dept = employee.department

    # ✅ Only show services from the moderator's department
    available_services = Service.objects.filter(department=dept)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        counter_number = request.POST.get('counter_number')
        selected_services = request.POST.getlist('services')


        # ✅ Generate secure password setup token
        token = secrets.token_urlsafe(32)

        # ✅ Create Counter (no password yet)
        counter = Counter.objects.create(
            name=name,
            email=email,
            password="",  # empty until they set it
            password_reset_token=token,
            counter_number=counter_number,
            department=dept
        )
        counter.services.set(selected_services)

        # ✅ Generate reset link for counter
        reset_link = request.build_absolute_uri(
            reverse('setpassword_counter', kwargs={'token': token})
        )

        # ✅ Send invitation email
        subject = "Set your Counter account password"
        html_content = f"""
            <p>Hello {name},</p>
            <p>You have been added as a Counter in the <strong>{dept.department_name}</strong> department.</p>
            <p>Click the link below to set your password and activate your account:</p>
            <p><a href="{reset_link}">Set Password</a></p>
            <p>If you did not expect this email, you can ignore it.</p>
        """
        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, f"Counter '{name}' invited! A password setup email has been sent.")
        return redirect('counter_list')


    return render(request, 'counter/add_counter.html', {
        'services': available_services,
        'department_name': dept.department_name,
          })

def setpassword_counter(request, token):
    """Counter sets password after invitation."""
    try:
        counter = Counter.objects.get(password_reset_token=token)
    except Counter.DoesNotExist:
        messages.error(request, "Invalid or expired token.")
        return redirect('login')  # adjust to your login URL name

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            counter.password = make_password(password)
            counter.password_reset_token = None
            counter.save()
            messages.success(request, "Password set successfully! You can now log in.")
            return redirect('login')  # adjust to your login URL name

    return render(request, 'counter/setpassword_counter.html', {'token': token})



def get_current_counter(request):
    return getattr(request, 'counter', None)

# ------------------------------
# Auto-assign tickets
# ------------------------------
def assign_next_ticket_auto():
    waiting_tickets = Ticket.objects.filter(status='Waiting').order_by('queue_position', 'created_at')

    for ticket in waiting_tickets:
        available_counters = Counter.objects.filter(
            services=ticket.service,
            status='Idle'
        ).order_by('counter_number')

        if available_counters.exists():
            counter = available_counters.first()
            ticket.status = 'Called'
            ticket.assigned_counter = counter
            ticket.save()
            counter.status = 'Serving'
            counter.save()


def services_dashboard(request):
    # ✅ Check if a counter is logged in
    counter_id = request.session.get("counter_id")
    if not counter_id:
        messages.error(request, "You must be logged in to access this page.")
        return redirect("login")

    # ✅ Fetch the counter object
    counter = get_object_or_404(Counter, pk=counter_id)

    # ✅ Restrict access to Counter #0 only
    if str(counter.counter_number) != "0":
        messages.warning(request, "You are not authorized to view this dashboard.")
        return redirect("counter_dashboard")

    # ✅ You can pass any data related to services or queues here
    # Example: show all services assigned to this counter’s department
    services = counter.department.service_set.all() if counter.department else []

    # ✅ Render services_dashboard.html
    return render(request, "services/service_dashboard.html", {
        "counter": counter,
        "services": services,
    })
@role_required('Counter')
def counter_dashboard(request):
    counter = get_current_counter(request)
    if not counter:
        messages.error(request, "Counter not found.")
        return redirect("login")

    # Get services assigned to this counter
    assigned_services = counter.services.all()

    # --- Update queue positions ---
    # Only for tickets in assigned services that are still waiting or skipped
    waiting_tickets = Ticket.objects.filter(
        service__in=assigned_services,
        status__in=['Waiting', 'Skipped']
    ).order_by('created_at')

    # Assign queue positions if not set
    for idx, t in enumerate(waiting_tickets, start=1):
        if not t.queue_position:
            t.queue_position = idx
            t.save()

    # --- Tickets for this counter ---
    # Show all tickets for the assigned services
    tickets = Ticket.objects.filter(
        service__in=assigned_services,
        status__in=['Waiting', 'Called', 'Skipped']
    ).order_by('queue_position')

    # --- Current ticket being served ---
    current_ticket = tickets.filter(status='Called').last()

    return render(request, 'counter/counter_dashboard.html', {
        'tickets': tickets,
        'current_ticket': current_ticket,
        'assigned_services': assigned_services,
        'counter_number': counter.counter_number,
    })

@role_required('Counter')
def call_next_ticket(request):
    if request.method != "POST":
        return redirect("counter_dashboard")

    counter = get_current_counter(request)
    if not counter:
        messages.error(request, "Counter not found.")
        return redirect("login")

    assigned_services = counter.services.all()

    # --- Mark current ticket as Served ---
    current_ticket = Ticket.objects.filter(
        assigned_counter=counter,
        status='Called'
    ).last()
    if current_ticket:
        current_ticket.status = 'Served'
        current_ticket.save()

    # --- Call next waiting ticket ---
    next_ticket = Ticket.objects.filter(
        service__in=assigned_services,
        status='Waiting'
    ).order_by('queue_position').first()

    if next_ticket:
        # Assign to this counter and update status
        next_ticket.status = 'Called'
        next_ticket.assigned_counter = counter
        next_ticket.save()
        messages.success(request, f"Now serving ticket {next_ticket.ticket_number}")
    else:
        messages.info(request, "No waiting tickets in your assigned services.")

    return redirect("counter_dashboard")

@role_required('Counter')
def skip_ticket(request, ticket_number):
    counter = get_current_counter(request)
    if not counter:
        messages.error(request, "Counter not found.")
        return redirect("login")

    assigned_services = counter.services.all()
    ticket = Ticket.objects.filter(ticket_number=ticket_number, service__in=assigned_services).first()
    if not ticket:
        messages.error(request, "Ticket not found or not in your assigned services.")
        return redirect("counter_dashboard")

    # Mark the ticket as Skipped
    ticket.status = 'Skipped'
    ticket.save()

    # Get all waiting or skipped tickets for this counter's services, ordered by queue_position
    waiting_tickets = list(Ticket.objects.filter(
        service__in=assigned_services,
        status__in=['Waiting', 'Skipped']
    ).order_by('queue_position'))

    if ticket in waiting_tickets:
        waiting_tickets.remove(ticket)
        # Insert skipped ticket into 3rd position if possible
        insert_index = min(2, len(waiting_tickets))  # 2 = third position (0-based)
        waiting_tickets.insert(insert_index, ticket)

    # Reassign queue positions sequentially
    for idx, t in enumerate(waiting_tickets, start=1):
        if t.queue_position != idx:
            t.queue_position = idx
            t.save()

    counter.status = 'Idle'
    counter.save()
    assign_next_ticket_auto()

    messages.success(request, f"Ticket {ticket.ticket_number} skipped and moved to 3rd position.")
    return redirect("counter_dashboard")

@role_required('Counter')
def back_to_queue(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    ticket.status = "Waiting"
    ticket.assigned_counter = None
    ticket.save()
    assign_next_ticket_auto()
    return redirect('counter_dashboard')

@role_required('Counter')
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
        counter.email = request.POST.get("email")
        counter.counter_number = request.POST.get("counter_number")

        # ✅ Get all selected service IDs from form
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



#RESET PASSWORD

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Check 1: Built-in Django admin user
        user = User.objects.filter(email=email).first()
        if user:
            token = get_random_string(50)
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', args=[token])
            )
            request.session[f'pwd_reset_{token}'] = {
                'user_type': 'admin',
                'user_id': user.id
            }

            send_mail(
                "Password Reset Request",
                f"Hi {user.username},\n\nClick the link to reset your password:\n{reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('login')

        # Check 2: Custom Moderator (Employee)
        employee = Employee.objects.filter(email=email).first()
        if employee:
            token = get_random_string(50)
            employee.password_reset_token = token
            employee.save()

            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', args=[token])
            )
            send_mail(
                "Password Reset Request",
                f"Hi {employee.name},\n\nClick the link to reset your password:\n{reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('login')

        # Check 3: Custom Counter
        counter = Counter.objects.filter(email=email).first()
        if counter:
            token = get_random_string(50)
            counter.password_reset_token = token
            counter.save()

            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', args=[token])
            )
            send_mail(
                "Password Reset Request",
                f"Hi {counter.name},\n\nClick the link to reset your password:\n{reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('login')

        # If email not found
        messages.error(request, "No account found with that email address.")
        return redirect('password_reset')

    return render(request, 'resetpassword/password_reset.html')


# =========================
# RESET PASSWORD PAGE
# =========================

def password_reset_confirm(request, token):
    # Try to find the user based on the token
    employee = Employee.objects.filter(password_reset_token=token).first()
    counter = Counter.objects.filter(password_reset_token=token).first()
    session_data = request.session.get(f'pwd_reset_{token}')

    if not employee and not counter and not session_data:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path)

        if employee:
            employee.password = new_password
            employee.password_reset_token = None
            employee.save()
        elif counter:
            counter.password = new_password
            counter.password_reset_token = None
            counter.save()
        else:
            from django.contrib.auth.hashers import make_password
            user = User.objects.get(id=session_data['user_id'])
            user.password = make_password(new_password)
            user.save()
            del request.session[f'pwd_reset_{token}']

        messages.success(request, "Your password has been reset successfully.")
        return redirect('login')

    return render(request, 'resetpassword/password_reset_confirm.html')

#TICKET DISPLAY VIEW

def ticket_display(request):
    tickets = Ticket.objects.filter(status__in=['Waiting','Called']).order_by('queue_position', 'created_at')
    return render(request, 'tickets_display.html', {'tickets': tickets})

def tickets_api(request):
    tickets = Ticket.objects.filter(status='Waiting').order_by('-created_at')
    data = [
        {
            'ticket_number': t.ticket_number,
            'counter_number': t.assigned_counter.counter_number if t.assigned_counter else 'N/A'
        }
        for t in tickets
    ]
    return JsonResponse(data, safe=False)
