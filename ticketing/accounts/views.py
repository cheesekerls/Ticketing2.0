# accounts/views.py
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

User = get_user_model()

def universal_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # ✅ Try Django built-in user (Moderator login using email)
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            request.session["email"] = user.email  
             # ✅ Debug session
           

            return redirect("moderator_dashboard")

        # ✅ Try custom Employee login (Admin & Staff)
        try:
            employee = Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, "login.html")

        if not check_password(password, employee.password):
            messages.error(request, "Invalid password")
            return render(request, "login.html")
         # ✅ Save session info
        request.session['employee_id'] = employee.employee_id
        request.session['employee_position'] = employee.position
        request.session['employee_department'] = (
            employee.department.department_id if employee.department else None
        )
        # ✅ Login custom employee
        request.session["email"] = employee.email

        # ✅ Redirect based on custom roles
        if employee.position == "Admin":
            return redirect("admin_dashboard", department_id=employee.department.department_id)
        elif employee.position == "Staff":
            return redirect("staff_dashboard")

        messages.error(request, "No dashboard assigned for this role")
        return render(request, "login.html")

    return render(request, "login.html")

def custom_logout(request):
    logout(request)  # Django logout clears auth
    request.session.flush()  # Clear custom session for Employee
    return redirect("login")


@role_required(["Moderator"])
def moderator_dashboard(request):
    return render(request, "Superadmin_dashboard.html")

@role_required(["Admin"])
@role_required('Admin')
@role_required('Admin')
@department_admin_required
def admin_dashboard(request, department_id):
    employee = Employee.objects.get(email=request.session.get("email"))
    department = employee.department

    return render(request, "admin_dashboard.html", {
        "employee": employee,
        "department": department
    })

@department_admin_required
def department_dashboard(request, department_id):
    # Only the admin of this department can view this
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

def delete_employee(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    return redirect('admin_list')


from .forms import AdminInviteForm

User = get_user_model()

def employee_list(request):
   return render(request, 'admin_employee.html')


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
        return redirect('employee_list')

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
        employee.password_reset_token = None  # Clear token after use
        employee.save()

        messages.success(request, "Password set successfully! You can now log in.")
        return redirect('login')

    return render(request, 'set_password.html', {'employee': employee})
