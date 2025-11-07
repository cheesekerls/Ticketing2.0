# ticketing/services/models.py
from django.db import models
from departments.models import Department

class CompServices(models.Model):
    comp_id = models.AutoField(primary_key=True)
    mac_address = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=100) 
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"Kiosk {self.comp_id} ({self.mac_address})"

class Service(models.Model): 
    id = models.AutoField(primary_key=True)
    service_id = models.IntegerField()
    service_name = models.CharField(max_length=100)
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('department', 'service_id')

    def __str__(self):
        return self.service_name
