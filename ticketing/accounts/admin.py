from django.contrib import admin
from django.db.models import Count, Q
from .models import Counter, Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'email', 'department', 'position', 'is_active', 'department_has_admin')
    list_filter = ('position', 'department', 'is_active')
    search_fields = ('name', 'email')
    ordering = ('department', 'position', 'name')

    # ✅ Annotate queryset to efficiently count Admins per department
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Annotate each employee with the number of admins in their department
        return qs.annotate(
            admin_count=Count('department__employee', filter=Q(department__employee__position='Admin'))
        )

    # ✅ Custom column to show if department already has an Admin
    def department_has_admin(self, obj):
        return "✅" if obj.admin_count > 0 else "❌"
    department_has_admin.short_description = "Dept Has Admin"
    department_has_admin.admin_order_field = 'admin_count'  # Allows sorting by this column

    # ✅ Optional: highlight rows where department already has an Admin
    def get_row_css(self, obj, index):
        # This method doesn’t exist by default; you need a custom template if you want actual color
        # Instead, we can style via list_display and HTML if desired
        return 'background-color: #e0ffe0;' if obj.admin_count > 0 else ''
@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    list_display = ('counter_id', 'email', 'counter_number', 'department')
    list_filter = ('department',)
    search_fields = ('counter_number', 'email')
    ordering = ('department', 'counter_number')