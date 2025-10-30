# ticketing/tickets/models.py
from django.db import models
from django.utils import timezone
from services.models import Service


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    ticket_number = models.CharField(max_length=20)
    lane= models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    queue_position = models.IntegerField(default=0)


    def __str__(self):
        return self.ticket_number


class Contact(models.Model):
    ticket = models.ForeignKey("tickets.Ticket", on_delete=models.CASCADE)
    email = models.EmailField()
    contact_no = models.CharField(max_length=20)

    def __str__(self):
        return f"Contact for {self.ticket.ticket_number}"


class ClaimedTicket(models.Model):
    ticket = models.ForeignKey("tickets.Ticket", on_delete=models.CASCADE)
    called_at = models.DateTimeField(auto_now_add=True)
    served_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Claimed Ticket #{self.ticket.ticket_number} - {self.status}"
