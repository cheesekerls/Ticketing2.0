from django.shortcuts import render, redirect, get_object_or_404
from .models import Service

def service_list(request):
    services = Service.objects.all()
    return render(request, 'service_list.html', {'services': services})

def add_service(request):
    if request.method == 'POST':
        name = request.POST.get('service_name')
        dept_id = request.POST.get('department_id')
        if name and dept_id:
            Service.objects.create(service_name=name, department_id=dept_id)
            return redirect('service_list')
    return render(request, 'add_service.html')

def manage_services(request):
    services = Service.objects.all()
    return render(request, 'manage_service.html', {'services': services})

def delete_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    service.delete()
    return redirect('manage_services')

def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.service_name = request.POST.get('service_name')
        service.save()
        return redirect('manage_services')
    return render(request, 'edit_service.html', {'service': service})
