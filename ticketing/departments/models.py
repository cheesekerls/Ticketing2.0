from django.db import models

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=200, unique=True)  # ✅ prevent duplicate names
    prefix = models.CharField(max_length=10)

    def __str__(self):
        # ✅ Just return its own name — not referencing non-existent fields
        return f"{self.department_name} ({self.prefix})"
