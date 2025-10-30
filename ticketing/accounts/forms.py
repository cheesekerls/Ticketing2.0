from django import forms
from django.contrib.auth import get_user_model
from departments.models import Department
from django.contrib.auth import password_validation

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

# ✅ Move this out as a separate, top-level class
class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter current password'}),
        required=True
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}),
        required=True,
        help_text=password_validation.password_validators_help_text_html()
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
        required=True
    )

    def __init__(self, admin_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_user = admin_user

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if not self.admin_user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("New passwords do not match.")
        password_validation.validate_password(new_password1, self.admin_user)
        return cleaned_data
