# accounts/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from departments.models import Department
from services.models import Service
from tickets.models import Ticket

User = get_user_model()

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    # optional employee relation (if you want to link a Django user -> employee)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# signal to create profile automatically
@receiver(post_save, sender=User)
def create_or_update_userprofile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # ensure profile exists on update
        UserProfile.objects.get_or_create(user=instance)


class AuthUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Counter(models.Model):
    counter_id = models.AutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    def __str__(self):
        # department referenced was missing in original __str__ — guard it
        dept_name = getattr(self.employee.department, 'name', getattr(self.employee.department, 'department_name', None))
        return f"{self.employee.name} - {dept_name}"
