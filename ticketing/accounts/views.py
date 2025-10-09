# accounts/views.py
import sys
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .models import Employee, Department
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages


class CustomLoginView(LoginView):
    template_name = "login.html"


    def get_success_url(self):
        user = self.request.user
        username = user.username.lower()

        # Redirect admins
        if username.endswith(".admin") and user.is_superuser:
            return "/accounts/admin/dashboard/"

        # Redirect staff
        elif username.endswith(".staff") and user.is_staff and not user.is_superuser:
            return "/accounts/staff/dashboard/"

        # Default fallback
        return "/"
    
@login_required
@user_passes_test(lambda u: u.is_superuser and u.username.endswith(".admin"))
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

# Staff dashboard (only staff with .staff username)
@login_required
@user_passes_test(lambda u: u.is_staff and not u.is_superuser and u.username.endswith(".staff"))
def staff_dashboard(request):
    return render(request, "staff_dashboard.html")


from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)  # Ends the session
    return redirect('login')  # Redirect to login page


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "staff_dashboard.html", {"employees": employees})


@login_required
@user_passes_test(lambda u: u.is_superuser and u.username.endswith(".admin"))
def add_staff(request):
    departments = Department.objects.all()

    # Debug: show request method
    print("🧩 DEBUG: add_staff view triggered with method:", request.method, file=sys.stderr)

    if request.method == 'POST':
        email = request.POST.get('email')
        department_id = request.POST.get('department')

        if not email or not department_id:
            messages.error(request, "Please fill all fields.")
            return redirect('add_staff')

        # Create user
        user, created = User.objects.get_or_create(username=email, email=email)
        if not created:
            messages.warning(request, "This email is already registered.")
            return redirect('add_staff')

        user.set_unusable_password()
        user.save()

        # Generate password reset link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = "127.0.0.1:8000"  # local dev
        reset_link = f"http://{domain}/reset/{uid}/{token}/"

        # Render email HTML
        html_content = render_to_string('emails/set_password_email.html', {
            'email': email,
            'reset_link': reset_link,
            'department_name': Department.objects.get(id=department_id).department_name,
        })

        # Prepare email
        subject = "Set Your Password for Staff Account"
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMultiAlternatives(subject, "", from_email, [email])
        msg.attach_alternative(html_content, "text/html")

        # Debug before sending
        print("🧩 DEBUG: Reached email section.", file=sys.stderr)
        print("📧 Sending email to:", email, file=sys.stderr)

        # Send email safely
        try:
            result = msg.send()
        except Exception as e:
            print("❌ Email sending failed:", e, file=sys.stderr)
            messages.error(request, f"Failed to send email: {e}")
        else:
            print("✅ Email sent successfully, result =", result, file=sys.stderr)
            messages.success(request, f"User created and email sent to {email}.")

        # Always redirect after POST
        return redirect('add_staff')

    # GET request → show form
    return render(request, 'add_staff_department.html', {'departments': departments})