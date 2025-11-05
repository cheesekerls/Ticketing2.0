from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Service
from accounts.models import Employee  # adjust if your Employee model is elsewhere
from accounts.decorators import role_required, department_admin_required

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
    """Add a new service under the logged-in employee's department."""
    email = request.session.get('email')
    if not email:
        return redirect('login')

    employee = get_object_or_404(Employee, email=email)
    dept = employee.department

    if request.method == 'POST':
        name = request.POST.get('service_name')

        if name:
            # Find next service_id for this department
            last_service = Service.objects.filter(department=dept).order_by('-service_id').first()
            next_id = (last_service.service_id + 1) if last_service else 1

            Service.objects.create(
                service_id=next_id,
                service_name=name,
                department=dept
            )
            return redirect('service_list')

    # Pass department name to the template
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
    """Allow deleting only if service belongs to employee’s department."""
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(Employee, pk=employee_id)
    service = get_object_or_404(Service, pk=service_id)

    # 🛑 Security check
    if service.department != employee.department:
        return HttpResponseForbidden("You don't have permission to delete this service.")

    service.delete()
    return redirect('service_list')