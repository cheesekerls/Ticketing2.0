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
    id = models.AutoField(primary_key=True)
    service_id = models.IntegerField()
    service_name = models.CharField(max_length=100)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE)
    comp = models.ForeignKey(
        'services.CompServices',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_service'
    )

    class Meta:
        unique_together = ('department', 'service_id')

    def __str__(self):
        # ✅ Use department_name instead of name
        return f"{self.service_name}"
