# ticketing/tickets/models.py
from django.db import models
from django.utils import timezone
from services.models import Service
from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    ticket_number = models.CharField(max_length=20)
    priority = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.ticket_number

# Contact information for the ticket
class Contact(models.Model):
    ticket = models.ForeignKey("tickets.Ticket", on_delete=models.CASCADE)
    email = models.EmailField()
    contact_no = models.CharField(max_length=20)


class ClaimedTicket(models.Model):
    ticket = models.ForeignKey("tickets.Ticket", on_delete=models.CASCADE)
    called_at = models.DateTimeField(auto_now_add=True)
    served_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50)
