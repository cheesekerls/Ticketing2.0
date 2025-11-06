from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from departments.models import Department
from .forms import DepartmentForm
from .forms import Department
from django.contrib import messages



def department_list(request):
    departments = Department.objects.all()
    return render(request, "department_list.html", {"departments": departments})


def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Department Added Successfully!")
            # ✅ redirect to your departments page instead of rendering dashboard
            return redirect("departments_list")
    else:
        form = DepartmentForm()
    
    return render(request, "add_department.html", {"form": form})
    

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


