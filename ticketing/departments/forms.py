from django import forms
from .models import Department
from services.models import Service

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'prefix', 'department_id']  # match model fields

    def clean_department_id(self):
        department_id = self.cleaned_data['department_id']
        if Department.objects.filter(department_id=department_id).exists():
            raise forms.ValidationError("Department ID already exists!")
        return department_id

    def clean_department_name(self):
        department_name = self.cleaned_data['department_name']
        # Case-insensitive check for duplicate names
        if Department.objects.filter(department_name__iexact=department_name).exists():
            raise forms.ValidationError("Department name already exists!")
        return department_name

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'department']

    def clean_service_name(self):
        service_name = self.cleaned_data.get('service_name')
        if Service.objects.filter(service_name__iexact=service_name).exists():
            raise forms.ValidationError("A service with this name already exists!")
        return service_name