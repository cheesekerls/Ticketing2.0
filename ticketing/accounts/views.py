# accounts/views.py
import sys
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

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = "login.html"

    # login redirect now configured in urls/settings to point to role redirect
    # or set LOGIN_REDIRECT_URL to '/redirect/' in settings.py


def role_redirect_view(request):
    # route users to dashboards by role
    if not request.user.is_authenticated:
        return redirect('login')

    profile = getattr(request.user, 'userprofile', None)
    role = getattr(profile, 'role', None)

    if role == 'moderator':
        return redirect('moderator_dashboard')
    elif role == 'Admin':
        return redirect('admin_dashboard')
    elif role == 'staff':
        return redirect('staff_dashboard')

    # fallback
    return redirect('login')


def custom_logout(request):
    logout(request)
    return redirect('login')


# role_required decorator helper
from functools import wraps
from django.http import HttpResponseForbidden

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            profile = getattr(request.user, 'userprofile', None)
            if not profile or profile.role != required_role:
                return HttpResponseForbidden("Access denied")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


@login_required
@role_required('moderator')
def moderator_dashboard(request):
    return render(request, "superadmin_dashboard.html")


@login_required
@role_required('Admin')
def admin_dashboard(request):
    # show only admin's department data if you want
    return render(request, "admin_dashboard.html")


@login_required
@role_required('staff')
def staff_dashboard(request):
    return render(request, "admin_dashboard.html")

@login_required
@role_required('moderator')
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "admin_list.html", {"employees": employees})


def update_employee(request):
    if request.method == 'POST':
        emp_id = request.POST.get('id')
        name = request.POST.get('name')
        department_name = request.POST.get('department')

        employee = get_object_or_404(Employee, pk=emp_id)

        employee.name = name

        try:
            department = Department.objects.get(department_name=department_name)
            employee.department = department
        except Department.DoesNotExist:
            messages.error(request, "Department not found.")
            return redirect('employee_list')

        employee.save()
        messages.success(request, "Employee updated successfully!")
        return redirect('employee_list')

    return redirect('employee_list')


def delete_employee(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    return redirect('employee_list')


from .forms import AdminInviteForm

User = get_user_model()

# Role decorator
def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            profile = getattr(request.user, 'userprofile', None)
            if not profile or profile.role != required_role:
                return HttpResponseForbidden("Access denied")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


@login_required
@role_required('moderator')
def add_admin(request):
    if request.method == 'POST':
        form = AdminInviteForm(request.POST)
    else:
        form = AdminInviteForm()

    # Make sure the queryset is fresh
    form.fields['department'].queryset = Department.objects.all()

    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        department = form.cleaned_data['department']

        # Create user
        user = User.objects.create(username=email, email=email, is_active=True)
        user.set_unusable_password()
        user.save()
        # Suppose `user` is your newly created admin
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

# Build the URL
        password_set_url = f"http://127.0.0.1:8000/set-password/{uid}/{token}/"
        subject = "Set your admin password"
        message = f"Hello {user.username},\n\nPlease set your password by clicking the link below:\n\n{password_set_url}\n\nThank you!"
        recipient_list = [user.email]

        send_mail(
         subject,
         message,
         settings.DEFAULT_FROM_EMAIL,
         recipient_list,
        fail_silently=False  # Shows errors if email fails
)

        # Create profile
        profile = UserProfile.objects.create(user=user, role='admin', department=department)

        # Create employee
        employee = Employee.objects.create(name=name, department=department, position='Admin')
        profile.employee = employee
        profile.save()

        # Generate password reset link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_path = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        reset_link = request.build_absolute_uri(reset_path)

        # Send email (console backend for testing)
        html_content = f"""
            <p>Hello {name},</p>
            <p>You have been invited as Admin in {department.department_name}.</p>
            <p>Click <a href="{reset_link}">here</a> to set your password.</p>
        """
        connection = get_connection(backend='django.core.mail.backends.console.EmailBackend')
        msg = EmailMultiAlternatives(
            subject="Set your Admin password",
            body="",
            from_email=None,
            to=[email],
            connection=connection
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, f"Admin {name} created! Check console for email.")
        return redirect('add_admin')

    return render(request, 'add_admin_department.html', {'form': form})
    
def set_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')  # Redirect after password set
        else:
            form = SetPasswordForm(user)
        return render(request, 'set_password.html', {'form': form})
    else:
        return render(request, 'invalid_link.html')
