from django.contrib import admin
from .models import Employee
from .models import Department

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id','department', 'name', 'position')
    list_filter = ('department',)
    search_fields = ('name', 'position')


