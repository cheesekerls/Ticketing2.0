from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket, ClaimedTicket
from .print_utils import print_ticket_to_pos as send_to_printer
from django.utils import timezone
from escpos.printer import Serial
import qrcode
from io import BytesIO
from services.models import CompServices, Service
import base64


def kiosk_home(request):
    """
    Display services assigned to this kiosk (office)
    """
    comp = get_kiosk_comp(request)
    if comp:
        services = Service.objects.filter(comp=comp)
    else:
        services = Service.objects.none()  # No services if kiosk not recognized

    return render(request, 'tickets/kiosk.html', {'services': services})


def get_kiosk_comp(request):
    """
    Detect the kiosk machine by IP.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    try:
        comp = CompServices.objects.get(ip_address=ip)
    except CompServices.DoesNotExist:
        comp = None
    return comp

import logging

logger = logging.getLogger(__name__)

def print_ticket_to_pos(request, service_id=None):
    """
    Create a ticket for a given service and lane (Regular/Priority),
    ensuring separate counters for each lane.
    """
    message = None
    comp = get_kiosk_comp(request)
    ticket_qr = None

    if request.method == 'POST':
        try:
            # Determine service
            post_service_id = request.POST.get('service_id')
            if post_service_id:
                service = get_object_or_404(Service, pk=int(post_service_id))
            elif service_id:
                service = get_object_or_404(Service, pk=service_id)
            else:
                service = Service.objects.first()

            if not service:
                return render(request, 'tickets/create_ticket.html', {
                    'error': 'No service defined. Please create a Service first.'
                })

            lane = request.POST.get('ticket_type', 'Regular')
            today = timezone.now().date()

            # ✅ Separate queue for Regular and Priority
            last_ticket = Ticket.objects.filter(
                service=service,
                comp=comp,
                lane=lane,
                created_at__date=today
            ).order_by('-queue_position').first()

            next_position = (last_ticket.queue_position + 1) if last_ticket else 1

            # ✅ Ticket number with lane prefix (R or P)
            ticket_number = f"{service.service_name[:3].upper()}-{lane[:1]}{next_position:03d}"

            # Create the ticket
            ticket = Ticket.objects.create(
                ticket_number=ticket_number,
                service=service,
                comp=comp,
                status='Waiting',
                lane=lane,
                queue_position=next_position,
                created_at=timezone.now()
            )

            # Generate QR code
            qr = qrcode.make(ticket.ticket_number)
            qr_io = BytesIO()
            qr.save(qr_io, format='PNG')
            ticket_qr = base64.b64encode(qr_io.getvalue()).decode()

            # Print to POS (if printer available)
            try:
                send_to_printer(
                    f"""
Ticket No: {ticket.ticket_number}
Service: {ticket.service.service_name}
Lane: {ticket.lane}
Status: {ticket.status}
Position: {ticket.queue_position}
""",
                    qr_data=ticket.ticket_number
                )
                message = f"Ticket {ticket.ticket_number} successfully printed!"
            except Exception as e:
                message = f"Ticket created but printing failed: {e}"

            # Optional logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Ticket {ticket.ticket_number} created for service {service.service_name} by kiosk {comp}")

        except Exception as e:
            message = f"Error: {e}"

    # Show only services for this kiosk
    if comp:
        services = Service.objects.filter(comp=comp)
    else:
        services = Service.objects.none()

    return render(request, 'tickets/create_ticket.html', {
        'services': services,
        'message': message,
        'ticket_qr': ticket_qr
    })


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
