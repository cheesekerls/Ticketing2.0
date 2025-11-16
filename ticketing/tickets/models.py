# ticketing/tickets/models.py
from django.db import models
from django.utils import timezone
from departments.models import Service
from departments.models import CompServices
# class Ticket(models.Model):

#     TICKET_STATUS = [
#         ('Waiting', 'Waiting'),
#         ('Called', 'Called'),
#         ('Served', 'Served'),
#         ('Skipped', 'Skipped'),
#         ('Cancelled', 'Cancelled')
#      ]

#     ticket_id = models.AutoField(primary_key=True)
#     ticket_number = models.CharField(max_length=20)
#     lane = models.CharField(max_length=50, blank=True, null=True)
#     status = models.CharField(max_length=20, choices=TICKET_STATUS, default='Waiting')
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     comp = models.ForeignKey(CompServices, on_delete=models.SET_NULL, null=True, blank=True)
#     assigned_counter = models.ForeignKey('accounts.Counter', null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tickets')
#     created_at = models.DateTimeField(default=timezone.now, editable=False)
#     queue_position = models.IntegerField(default=0)
   
#     def __str__(self):
#         return self.ticket_number

class Ticket(models.Model):
    TICKET_STATUS = [
        ('Waiting', 'Waiting'),
        ('Called', 'Called'),
        ('Served', 'Served'),
        ('Skipped', 'Skipped'),
        ('Cancelled', 'Cancelled'),
    ]

    ticket_id = models.AutoField(primary_key=True)
    ticket_number = models.CharField(max_length=20)
    lane = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='Waiting')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    comp = models.ForeignKey(CompServices, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_counter = models.ForeignKey(
        'accounts.Counter',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets'
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    start_time = models.DateTimeField(null=True, blank=True)  # ✅ Add served_at
    end_time = models.DateTimeField(null=True, blank=True)   # ✅ Add ended_at  
    queue_position = models.IntegerField(default=0)
    issued_date = models.DateField(default=timezone.now)  # ✅ Add this

    class Meta:
        unique_together = ('service', 'ticket_number', 'issued_date')  # ✅ Prevent duplicates

    def __str__(self):
        return self.ticket_number


class Contact(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    email = models.EmailField()
    contact_no = models.CharField(max_length=20)

    def __str__(self):
        return f"Contact for {self.ticket.ticket_number}"


class ClaimedTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    called_at = models.DateTimeField(auto_now_add=True)
    served_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Claimed Ticket #{self.ticket.ticket_number} - {self.status}"
