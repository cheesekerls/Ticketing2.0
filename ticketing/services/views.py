from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Service
from accounts.models import Employee  # adjust if your Employee model is elsewhere
from accounts.decorators import role_required, department_admin_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


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
        context['admin_dashboard'] = True

    return render(request, 'service_list.html', context)



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

    return render(request, 'add_service.html', {'department_name': dept.department_name})


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

    return render(request, 'edit_service.html', {'service': service})


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
<<<<<<< HEAD

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    else:
        return redirect('service_list')
    
@csrf_exempt
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
=======
    return redirect('service_list')

    
>>>>>>> 7f3ae303ec1a32272dd33bb3630375691e77c039
