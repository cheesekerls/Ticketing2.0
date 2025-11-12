# accounts/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from departments.models import Department
from departments.models import Service
from tickets.models import Ticket
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.db.models import Q

User = get_user_model()

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=50)
    password = models.CharField(max_length=255, null=True, blank=True)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def clean(self):
        # Prevent multiple Moderators in the same department
        if self.position == 'Moderator':
            existing_moderator = Employee.objects.filter(
                position='Moderator',
                department=self.department
            ).exclude(pk=self.pk)
            if existing_moderator.exists():
                raise ValidationError(f"An Moderator for '{self.department.department_name}' already exists.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.position})"

    # ✅ Place Meta at the end of the model
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['department'],
                condition=Q(position='Moderator'),
                name='unique_moderator_per_department'
            )
        ]
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('counter', 'Counter'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    # optional employee relation (if you want to link a Django user -> employee)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')
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




    def __str__(self):
        return f"{self.username} ({self.department})"

class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    def __str__(self):
        # department referenced was missing in original __str__ — guard it
        dept_name = getattr(self.employee.department, 'name', getattr(self.employee.department, 'department_name', None))
        return f"{self.employee.name} - {dept_name}"






class Counter(models.Model):
    counter_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    counter_number = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, default='Idle')  # Idle / Serving


    # ✅ Admin can assign multiple services per counter
    services = models.ManyToManyField(Service, blank=True)

    def __str__(self):
        return f"{self.email} - Counter {self.counter_number}"

    class Meta:
        verbose_name = "Counter"
        verbose_name_plural = "Counters"
