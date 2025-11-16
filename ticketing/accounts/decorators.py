from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from accounts.models import Employee, UserProfile, Counter

from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from accounts.models import Employee, UserProfile, Counter


def role_required(allowed_roles):
    """
    Decorator to restrict access by role: Moderator, Admin, Staff, Counter.
    Supports Django User, Employee, and Counter sessions.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            # 1️⃣ Django User (Admin)
            if request.user and not isinstance(request.user, AnonymousUser):
                try:
                    profile = UserProfile.objects.get(user=request.user)
                    if profile.role.capitalize() in [r.capitalize() for r in allowed_roles]:
                        return view_func(request, *args, **kwargs)
                    else:
                        messages.error(request, "Access denied for your role.")
                        return redirect('forbidden')
                except UserProfile.DoesNotExist:
                    pass

            # 2️⃣ Employee session (Moderator / Staff)
            email = request.session.get("email")
            if email:
                try:
                    employee = Employee.objects.get(email=email)
                    if employee.position.capitalize() in [r.capitalize() for r in allowed_roles]:
                        return view_func(request, *args, **kwargs)
                    else:
                        return HttpResponseForbidden("Access denied for your role.")
                except Employee.DoesNotExist:
                    pass

            # 3️⃣ Counter session (Queue users)
            counter_id = request.session.get("counter_id")
            if counter_id:
                try:
                    # make sure it's int-safe
                    counter = get_object_or_404(Counter, pk=int(counter_id))
                    request.counter = counter
                    if "Counter".capitalize() in [r.capitalize() for r in allowed_roles]:
                        return view_func(request, *args, **kwargs)
                    
                    else:
                        return HttpResponseForbidden("Access denied for your role.")
                except Exception as e:
                    messages.error(request, f"Counter not found ({e}).")
                    return redirect("login")

            # 4️⃣ Not logged in at all
            messages.error(request, "Please log in to continue.")
            return redirect("login")

        return _wrapped
    return decorator


    # def decorator(view_func):
    #     @wraps(view_func)
    #     def _wrapped(request, *args, **kwargs):
    #         # 1️⃣ Django User (Admin)
    #         if request.user and not isinstance(request.user, AnonymousUser):
    #             try:
    #                 profile = UserProfile.objects.get(user=request.user)
    #                 if profile.role.capitalize() in [r.capitalize() for r in allowed_roles]:
    #                     return view_func(request, *args, **kwargs)
    #                 else:
    #                     messages.error(request, "Access denied for your role.")
    #                     return redirect('forbidden')
    #             except UserProfile.DoesNotExist:
    #                 pass

    #         # 2️⃣ Employee session (Moderator / Staff)
    #         email = request.session.get("email")
    #         if email:
    #             try:
    #                 employee = Employee.objects.get(email=email)
    #                 if employee.position.capitalize() in [r.capitalize() for r in allowed_roles]:
    #                     return view_func(request, *args, **kwargs)
    #                 else:
    #                     return HttpResponseForbidden("Access denied for your role.")
    #             except Employee.DoesNotExist:
    #                 pass

    #         # 3️⃣ Counter session (Queue users)
    #         counter_id = request.session.get("counter_id")
    #         if counter_id:
    #             try:
    #                 counter = get_object_or_404(Counter, pk=int(counter_id))
    #                 request.counter = counter

    #                 # ✅ Automatically redirect kiosks (counter_number == 0)
    #                 if counter.counter_number == 0:
    #                     return redirect('service_dashboard')  # 👈 this is your kiosk page

    #                 if "Counter".capitalize() in [r.capitalize() for r in allowed_roles]:
    #                     return view_func(request, *args, **kwargs)
    #                 else:
    #                     return HttpResponseForbidden("Access denied for your role.")

    #             except Exception as e:
    #                 messages.error(request, f"Counter not found ({e}).")
    #                 return redirect("login")

    #         # 4️⃣ Not logged in at all
    #         messages.error(request, "Please log in to continue.")
    #         return redirect("login")

    #     return _wrapped
    # return decorator


def department_moderator_required(view_func):
    """
    Ensures only moderators (or admins) of their assigned department can access.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):

        # Admin user (Django User)
        if request.user and not isinstance(request.user, AnonymousUser):
            try:
                profile = UserProfile.objects.get(user=request.user)
                if profile.role.lower() == "admin":
                    return view_func(request, *args, **kwargs)
            except UserProfile.DoesNotExist:
                pass

        # Employee session check
        email = request.session.get("email")
        if not email:
            messages.error(request, "You must log in first.")
            return redirect("login")

        try:
            employee = Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            messages.error(request, "Access denied: You are not a valid employee.")
            return redirect("login")

        if employee.position.lower() != "Moderator":
            messages.error(request, "Access denied: Only moderators can access this section.")
            return redirect("forbidden")

        # Attach department to request
        request.department = employee.department

        return view_func(request, *args, **kwargs)


