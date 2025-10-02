# ticketing/services/models.py
from django.db import models
from departments.models import Department

class CompServices(models.Model):
    comp_id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=50)
    mac_address = models.CharField(max_length=50)

    def __str__(self):
        return str(self.comp_id)

class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    comp = models.ForeignKey(
        CompServices,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_service'
    )

    def __str__(self):
        return self.service_name
