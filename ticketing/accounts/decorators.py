from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from accounts.models import Employee, UserProfile


def role_required(allowed_roles):
    """Decorator to restrict access by user role (Moderator, Admin, Staff)."""
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]  # support single role

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):

            # ✅ 1. Moderator (Django user)
            if request.user and not isinstance(request.user, AnonymousUser):
                try:
                    profile = UserProfile.objects.get(user=request.user)
                    if profile.role.capitalize() in [r.capitalize() for r in allowed_roles]:
                        return view_func(request, *args, **kwargs)
                    else:
                        messages.error(request, "Access denied for your role.")
                        return redirect('forbidden')
                except UserProfile.DoesNotExist:
                    pass  # fall through to Employee check

            # ✅ 2. Admin / Staff (Employee-based login)
            email = request.session.get("email")
            if email:
                try:
                    employee = Employee.objects.get(email=email)
                    if employee.position.capitalize() in [r.capitalize() for r in allowed_roles]:
                        return view_func(request, *args, **kwargs)
                    else:
                        return HttpResponseForbidden("Access denied for your role.")
                except Employee.DoesNotExist:
                    messages.error(request, "User not found.")
                    return redirect("login")

            # ✅ 3. Not logged in at all
            messages.error(request, "Please log in to continue.")
            return redirect("login")

        return _wrapped
    return decorator



def department_admin_required(view_func):
    """Ensures only the admin of their assigned department can access."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):

        # ✅ Allow Moderators full access
        if request.user and not isinstance(request.user, AnonymousUser):
            try:
                profile = UserProfile.objects.get(user=request.user)
                if profile.role.lower() == "moderator":
                    return view_func(request, *args, **kwargs)
            except UserProfile.DoesNotExist:
                pass

        # ✅ For Admin/Employee session logins
        email = request.session.get("email")
        if not email:
            messages.error(request, "You must log in first.")
            return redirect("login")

        try:
            employee = Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            messages.error(request, "Access denied: You are not a valid employee.")
            return redirect("login")

        # ✅ Check if Admin position
        if employee.position.lower() != "admin":
            messages.error(request, "Access denied: Only admins can access this section.")
            return redirect("forbidden")

        # ✅ Optionally attach department to request for convenience
        request.department = employee.department

        return view_func(request, *args, **kwargs)

    return _wrapped
