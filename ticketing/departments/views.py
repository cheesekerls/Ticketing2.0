from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from departments.models import Department
from .forms import DepartmentForm
from .forms import Department
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import role_required

@login_required
@role_required('Moderator')
def department_list(request):
    departments = Department.objects.all()
    return render(request, "department_list.html", {"departments": departments})

@login_required
@role_required('Moderator')
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


