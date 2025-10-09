

# Register your models here.
from django.contrib import admin
from .models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("department_id", "department_name", "prefix")
    search_fields = ("department_name", "prefix")
    ordering = ("department_name",)
    
admin.site.site_header = "Ticketing System Administration"
admin.site.site_title = "Ticketing Admin Portal"