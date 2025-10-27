from django import forms
from django.contrib.auth import get_user_model
from departments.models import Department

User = get_user_model()

class AdminInviteForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'admin@example.com'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="-- Select Department --",
        required=True
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
      
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),  # will filter later in the view
        required=True
    )
