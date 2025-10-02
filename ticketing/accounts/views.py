# accounts/views.py
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test

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