from django.db import models
from departments.models import Department
from services.models import Service
from tickets.models import Ticket


class Counter(models.Model):
    counter_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)
    counter_number = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)

    # ✅ Admin can assign multiple services per counter
    services = models.ManyToManyField(Service, blank=True)

    def __str__(self):
        return f"{self.email} - Counter {self.counter_number}"

    class Meta:
        verbose_name = "Counter"

        verbose_name_plural = "Counters"

        verbose_name_plural = "Counters"

