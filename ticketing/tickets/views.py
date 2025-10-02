from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket, ClaimedTicket

def create_ticket(request, service_id=None):
    if request.method == 'POST':
        ticket_number = request.POST.get('ticket_number')
        if ticket_number:
            ticket = Ticket.objects.create(ticket_number=ticket_number, service_id=service_id)
            return redirect('queue_status', ticket_number=ticket.ticket_number)
    return render(request, 'tickets/create_ticket.html')

def queue_status(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    return render(request, 'tickets/queue_status.html', {'ticket': ticket})

def ticket_detail(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

def manage_queue(request):
    tickets = Ticket.objects.all().order_by('created_at')
    return render(request, 'tickets/manage_queue.html', {'tickets': tickets})

def service_actions(request, service_id):
    return render(request, 'tickets/service_actions.html', {'service_id': service_id})

def mark_served(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.status = "Served"
    ticket.save()
    return redirect('manage_queue')

def skip_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.status = "Skipped"
    ticket.save()
    return redirect('manage_queue')

def serve_skipped(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.status = "Served"
    ticket.save()
    return redirect('manage_queue')

def mark_missed(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.status = "Missed"
    ticket.save()
    return redirect('manage_queue')

def end_session(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.status = "Ended"
    ticket.save()
    return redirect('manage_queue')

def history_view(request):
    tickets = Ticket.objects.all()
    return render(request, 'tickets/history.html', {'tickets': tickets})

def scan_qrcode(request):
    return render(request, 'tickets/scan_qrcode.html')
