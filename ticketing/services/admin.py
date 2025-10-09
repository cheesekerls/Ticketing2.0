from django.contrib import admin
from .models import CompServices, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_id', 'service_name', 'department', 'comp')
    list_filter = ('department',)
    search_fields = ('service_name',)
