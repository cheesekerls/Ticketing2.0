from django.shortcuts import render, get_object_or_404, redirect
from tickets.models import Ticket  # adjust this import if your Ticket model is elsewhere
from django.http import JsonResponse
from django.db import models
from django.views.decorators.http import require_GET

@require_GET
def queue_status_ajax(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    # Count tickets ahead
    people_ahead_count = Ticket.objects.filter(
        service=ticket.service,
        lane=ticket.lane,
        status__in=['Waiting', 'Called']
    ).filter(
        models.Q(created_at__lt=ticket.created_at) |
        models.Q(created_at=ticket.created_at, ticket_id__lt=ticket.ticket_id)
    ).count()

    return JsonResponse({
        "status": ticket.status,
        "people_ahead_count": people_ahead_count,
        "counter": ticket.counter if hasattr(ticket, "counter") else None
    })


def user_home(request):
    return render(request, 'user/user_home.html')


def queue_status_redirect(request):
    ticket_number = request.GET.get('ticket_number')
    if ticket_number:
        return redirect('queue_status', ticket_number=ticket_number)
    return redirect('user_home')


def queue_status(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    people_ahead_count = Ticket.objects.filter(
    service=ticket.service,
    lane=ticket.lane,
    status__in=['Waiting', 'Called'],
    queue_position__lt=ticket.queue_position
    ).count()


    context = {
        'ticket': ticket,
        'people_ahead_count': people_ahead_count,
    }
    return render(request, 'user/queue_status.html', context)



def scan_qrcode(request):
    return render(request, 'user/scan_qrcode.html')

def cancel_ticket(request, ticket_number):
    if request.method == "POST":
        try:
            ticket = Ticket.objects.get(ticket_number=ticket_number)  # use ticket_number instead of id
            ticket.status = "Cancelled"
            ticket.save()
            return JsonResponse({"success": True})
        except Ticket.DoesNotExist:
            return JsonResponse({"success": False, "error": "Ticket not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})
