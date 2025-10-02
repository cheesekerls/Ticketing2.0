from django.shortcuts import render, redirect
from departments.models import Department
from .forms import DepartmentForm
from .forms import Department
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'department_list.html', {'departments': departments})


def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')  # change if you have a list page
    else:
        form = DepartmentForm()
    return render(request, 'add_department.html', {'form': form})
