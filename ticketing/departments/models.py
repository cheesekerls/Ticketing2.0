from django.db import models

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100, unique=True)  # ✅ prevent duplicate names
    prefix = models.CharField(max_length=10)

    def __str__(self):
        return self.department_name
