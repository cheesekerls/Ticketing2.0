from django.db import models

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=200, unique=True)  # ✅ prevent duplicate names
    prefix = models.CharField(max_length=10)

    def __str__(self):
        # ✅ Just return its own name — not referencing non-existent fields
        return f"{self.department_name} ({self.prefix})"


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


class CompServices(models.Model):
    comp_id = models.AutoField(primary_key=True)
    mac_address = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=100) 
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"Kiosk {self.comp_id} ({self.mac_address})"
