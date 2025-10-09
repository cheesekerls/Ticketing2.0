from django import forms
from .models import Department

class DepartmentForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width:100%; margin-bottom:15px; padding:8px;'})
    )
 