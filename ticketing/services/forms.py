# services/forms.py
from django import forms
from .models import CompServices

class CompServicesForm(forms.ModelForm):
    class Meta:
        model = CompServices
        fields = ['mac_address', 'role', 'department']
        widgets = {
            'mac_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter MAC Address'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Role'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }
