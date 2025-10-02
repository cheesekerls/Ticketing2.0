from django import forms
from .models import Department
from services.models import Service

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = [ 'department_name']

    def clean_department_id(self):
        department_id = self.cleaned_data['department_id']
        if Department.objects.filter(department_id=department_id).exists():
            raise forms.ValidationError("Department ID already exists!")
        return department_id

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name','department']  # match model fields
    
    def clean(self):
        cleaned_data = super().clean()
        service_name = cleaned_data.get("service_name")
 
        if Service.objects.filter(service_name=service_name).exists():
            raise forms.ValidationError("A service with this name already exists!")
