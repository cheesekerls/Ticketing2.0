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
from accounts.decorators import department_admin_required, role_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout
import secrets
from accounts.models import Employee as StaffEmployee  # rename to avoid clash
from .forms import ChangePasswordForm
from accounts.models import Employee  # or your Admin user model
from services.models import Service
from counter.models import Counter
from tickets.models import Ticket
from datetime import date
import json
from django.db.models import Count
from django.http import HttpResponse
import csv
from django.utils.timezone import now


User = get_user_model()


def universal_login(request):
    if request.method == "POST":
        identifier = request.POST.get("email")  # can be email OR username
        password = request.POST.get("password")

        # ========== 1️⃣ MODERATOR (Django built-in User) ==========
        user = None
        try:
            # detect if identifier looks like an email
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
            return redirect("moderator_dashboard")

        # ========== 2️⃣ EMPLOYEE (Admin / Staff) ==========
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

            if employee.position == "Admin":
                return redirect("admin_dashboard")
            elif employee.position == "Staff":
                return redirect("staff_dashboard")
            else:
                messages.error(request, "No dashboard assigned for this role.")
                return render(request, "login.html")

        # ========== 3️⃣ COUNTER (Queue Users) ==========
        counter = None
        try:
            if "@" in identifier and hasattr(Counter, "email"):
                counter = Counter.objects.filter(email=identifier).first()
        except Exception:
            counter = None

        if counter:
            # support both hashed and plain passwords
              if check_password(password, counter.password) or counter.password == password:
                request.session["email"] = counter.email  # use email as identifier
                return redirect("queue_dashboard")

        # ========== ❌ NO MATCH ==========
        messages.error(request, "Invalid username/email or password")
        return render(request, "login.html")

    return render(request, "login.html")

def custom_logout(request):
    logout(request)
    request.session.flush()
    return redirect("login")

@role_required(["Moderator"])
def moderator_dashboard(request):
    total_departments = Department.objects.count()
    total_admins = Employee.objects.filter(position='Admin').count()  # assuming position='admin'

    # For chart
    departments = Department.objects.all()
    department_labels = [dept.department_name for dept in departments]
    admins_counts = [Employee.objects.filter(position='Admin', department=dept).count() for dept in departments]

    # Get all admins for table
    admins = Employee.objects.filter(position='Admin').select_related('department')

    context = {
        'total_departments': total_departments,
        'total_admins': total_admins,
        'department_labels': department_labels,
        'admins_counts': admins_counts,
        'admins': admins
    }

    return render(request, 'superadmin_dashboard.html', context)
@role_required('Admin')
@department_admin_required
def admin_dashboard(request):
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
    return render(request, 'admin_dashboard.html', context)



@department_admin_required
def department_dashboard(request, department_id):
    employee = Employee.objects.get(email=request.session.get("email"))
    return render(request, 'admin_dashboard.html', {"employee": employee})


@role_required(["Staff"])
def staff_dashboard(request):
    return render(request, "staff_dashboard.html")


@role_required("Moderator")
def admin_list(request):
    employees = Employee.objects.all()
    return render(request, "admin_list.html", {"employees": employees})


def forbidden_view(request):
    return render(request, '403.html', status=403)


def edit_employee(request):
    if request.method == 'POST':
        emp_id = request.POST.get('id')
        employee = get_object_or_404(Employee, pk=emp_id)
        employee.name = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.department = request.POST.get('department_name')
        messages.success(request, "Employee updated successfully!")
        employee.save()

    return redirect('admin_list')

def admin_change_password(request):
    user_id = request.session.get('employee_id')  # your custom admin session
    if not user_id:
        return redirect('login')

    user = Employee.objects.get(pk=user_id)

    if request.method == "POST":
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, "Password updated successfully!")
            return redirect('admin_dashboard')
    else:
        form = ChangePasswordForm(user)

    return render(request, 'change_password.html', {'form': form})


def delete_employee(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    return redirect('admin_list')



def reports(request):
    return render(request, 'reports.html')


@login_required
@role_required('Moderator')
def add_admin(request):
    if request.method == 'POST':
        form = AdminInviteForm(request.POST)
    else:
        form = AdminInviteForm()

    departments_with_admin = Employee.objects.filter(position='Admin').values_list('department_id', flat=True)

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
            position="Admin",
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
        subject = "Set your Admin account password"
        html_content = f"""
            <p>Hello {name},</p>
            <p>You have been added as an Admin in <strong>{department.department_name}</strong>.</p>
            <p>Click the link below to set your password and activate your account:</p>
            <p><a href="{reset_link}">Set Password</a></p>
            <p>If you did not expect this email, you can ignore it.</p>
        """
        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, f"Admin '{name}' invited! A password setup email has been sent.")
        return redirect('admin_list')

    return render(request, 'add_admin_department.html', {'form': form})


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

    return render(request, 'set_password.html', {'employee': employee})

@role_required('Admin')
@department_admin_required
def counter_list(request):
    employee = Employee.objects.get(pk=request.session.get("employee_id"))
    counters = Counter.objects.filter(department=employee.department)

    context = {
        'counters': counters
    }
    return render(request, 'counter_list.html', context)


def report_dashboard(request):
    today = now().date()
    month = today.month
    year = today.year

    # ✅ Count tickets (daily, monthly, yearly)
    today_tickets = Ticket.objects.filter(created_at__date=today).count()
    monthly_tickets = Ticket.objects.filter(created_at__year=year, created_at__month=month).count()
    yearly_tickets = Ticket.objects.filter(created_at__year=year).count()
    total_tickets = Ticket.objects.count()

    # ✅ Ticket count per service
    service_summary = (
        Ticket.objects.values('service__service_name')
        .annotate(total=Count('ticket_id'))
        .order_by('-total')
    )

    # ✅ Ticket count per department (optional)
   
    # ✅ Data for chart
    monthly_data = (
        Ticket.objects.filter(created_at__year=year)
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
    }

    return render(request, 'admin_reports.html', context)