from django.db import models
from departments.models import Department
from services.models import Service
from tickets.models import Ticket


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class AuthUser(models.Model):   
    user_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)


class Counter(models.Model):
    counter_id = models.AutoField(primary_key=True)
    counter_number = models.CharField(max_length=100)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='accounts_counters'
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='accounts_counters_tickets'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        db_column='service_id',
        null=True,
        blank=True,
        related_name='accounts_counters_services'
    )

    def __str__(self):
        return f"{self.counter_number} ({self.department})"


class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee.name} - {self.ticket.id}"
