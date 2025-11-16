from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from departments.models import Department
from .forms import DepartmentForm
from .forms import Department
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import role_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Service
from accounts.models import Employee  # adjust if your Employee model is elsewhere
from accounts.decorators import role_required, department_moderator_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CompServices, Department
from django.contrib.auth.decorators import login_required
from .forms import CompServicesForm

@login_required
@role_required('Admin')
def department_list(request):
    departments = Department.objects.all()
    return render(request, "department_list.html", {"departments": departments})

@login_required
@role_required('Admin')
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Department Added")
            return redirect("department_list")
        else:
            # Form is invalid (e.g., duplicate department name)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)  # Show error messages

    else:
        form = DepartmentForm()

    # Render the form template with errors if any
    return render(request, "add_department.html", {"form": form})

@login_required
@role_required('Admin')
def check_department_name(request):
    name = request.GET.get('name', '').strip()
    exists = Department.objects.filter(department_name__iexact=name).exists()
    return JsonResponse({'exists': exists})   

def update_department(request):
    if request.method == 'POST':
        dept_id = request.POST.get('department_id')
        dept = get_object_or_404(Department, pk=dept_id)
        dept.department_name = request.POST.get('department_name')
        dept.prefix = request.POST.get('prefix')
        dept.save()
    return redirect('department_list')

def delete_department(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    department.delete()
    messages.success(request, "Department deleted successfully!")
    return redirect('department_list')



def service_list(request):
    """Show only services from the logged-in employee's department."""
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(Employee, pk=employee_id)
    services = Service.objects.filter(department=employee.department)

    context = {
        'services': services,
        'user_department': employee.department,
    }

    # Full page render
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        context['moderator/moderator_dashboard'] = True

    return render(request, 'services/service_list.html', context)

def add_service(request):
    """Add multiple unique services under the logged-in employee's department."""
    email = request.session.get('email')
    if not email:
        return redirect('login')

    employee = get_object_or_404(Employee, email=email)
    dept = employee.department

    if request.method == 'POST':
        service_names = request.POST.getlist('service_name[]')
        created_count = 0
        duplicates = []

        for name in service_names:
            name = name.strip()
            if not name:
                continue

            # ✅ Check if service already exists in the same department
            exists = Service.objects.filter(
                department=dept,
                service_name__iexact=name  # case-insensitive check
            ).exists()

            if exists:
                duplicates.append(name)
                continue

            # ✅ Assign next service_id
            last_service = Service.objects.filter(department=dept).order_by('-service_id').first()
            next_id = (last_service.service_id + 1) if last_service else 1

            Service.objects.create(
                service_id=next_id,
                service_name=name,
                department=dept
            )
            created_count += 1

        # ✅ Feedback messages
        if created_count > 0:
            messages.success(request, f"{created_count} service(s) successfully added.")
        if duplicates:
            messages.warning(request, f"Skipped duplicates: {', '.join(duplicates)}")

        return redirect('add_service')

    return render(request, 'services/add_service.html', {'department_name': dept.department_name})

@login_required
@role_required('Moderator')
def edit_service(request, pk):
    """Allow editing only if the service belongs to employee’s department."""
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(Employee, pk=employee_id)
    service = get_object_or_404(Service, pk=pk)

    # 🛑 Security check
    if service.department != employee.department:
        return HttpResponseForbidden("You don't have permission to edit this service.")

    if request.method == 'POST':
        service.service_name = request.POST.get('service_name')
        service.save()
        return redirect('service_list')

    return render(request, 'services/edit_service.html', {'service': service})

@login_required
@role_required('Moderator')
def delete_service(request, service_id):
    """Delete service securely — supports AJAX."""
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    employee = get_object_or_404(Employee, pk=employee_id)
    service = get_object_or_404(Service, pk=service_id)

    if service.department != employee.department:
        return HttpResponseForbidden("You don't have permission to delete this service.")

    service.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    else:
        return redirect('service_list')
    
@csrf_exempt
@login_required
@role_required('Moderator')
def delete_multiple_services(request):
    """Delete multiple services safely."""
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request'}, status=400)

    employee_id = request.session.get('employee_id')
    if not employee_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    employee = get_object_or_404(Employee, pk=employee_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
        ids = data.get('ids', [])
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # delete only services under employee's department
    services = Service.objects.filter(id__in=ids, department=employee.department)
    count = services.count()
    services.delete()

    return JsonResponse({'success': True, 'deleted': count})

@login_required
@role_required('Moderator')
def check_service_duplicate(request):
    """AJAX: Check if a service name already exists in this employee's department."""
    email = request.session.get('email')
    if not email:
        return JsonResponse({'error': 'not_logged_in'}, status=401)

    employee = get_object_or_404(Employee, email=email)
    dept = employee.department

    service_name = request.GET.get('name', '').strip()

    if not service_name:
        return JsonResponse({'exists': False})

    exists = Service.objects.filter(
        department=dept,
        service_name__iexact=service_name
    ).exists()

    return JsonResponse({'exists': exists})



# @login_required
# @role_required('Admin')
# def machine_kiosk_view(request):
#     """
#     Display all kiosks and handle adding a new kiosk via form.
#     """
#     kiosks = CompServices.objects.select_related('department').all()

#     if request.method == "POST":
#         form = CompServicesForm(request.POST)
#         if form.is_valid():
#             # ✅ Cleaned data
#             mac_address = form.cleaned_data['mac_address']
#             role = form.cleaned_data['role']
#             department = form.cleaned_data['department']

#             # ✅ Ensure no duplicate MAC
#             if CompServices.objects.filter(mac_address=mac_address).exists():
#                 messages.error(request, f"Kiosk with MAC {mac_address} already exists.")
#             else:
#                 CompServices.objects.create(
#                     mac_address=mac_address,
#                     role=role,
#                     department=department
#                 )
#                 messages.success(request, "Machine/Kiosk added successfully!")
#                 return redirect('machine_kiosk')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = CompServicesForm()

#     context = {
#         'form': form,
#         'kiosks': kiosks
#     }
#     return render(request, 'machine/machine_kiosk.html', context)


# @login_required
# @role_required('Admin')
# def update_kiosk(request, comp_id):
#     kiosk = get_object_or_404(CompServices, comp_id=comp_id)

#     if request.method == "POST":
#         mac_address = request.POST.get('mac_address', '').strip()
#         role = request.POST.get('role', '').strip()

#         if not mac_address or not role:
#             messages.error(request, "MAC Address and Role are required.")
#             return redirect('machine_kiosk')

#         # Prevent duplicate MAC for other kiosks
#         if CompServices.objects.exclude(comp_id=kiosk.comp_id).filter(mac_address=mac_address).exists():
#             messages.error(request, f"MAC {mac_address} is already used by another kiosk.")
#             return redirect('machine_kiosk')

#         try:
#             kiosk.mac_address = mac_address
#             kiosk.role = role
#             # department remains unchanged
#             kiosk.save()
#             messages.success(request, "Machine/Kiosk updated successfully!")
#         except Exception as e:
#             messages.error(request, f"Error updating kiosk: {e}")

#     return redirect('machine_kiosk')
# @login_required
# @role_required('Admin')
# def delete_kiosk(request, comp_id):
#     """
#     Delete a kiosk safely.
#     """
#     kiosk = get_object_or_404(CompServices, pk=comp_id)
#     kiosk.delete()
#     messages.success(request, "Machine/Kiosk deleted successfully!")
#     return redirect('machine_kiosk')