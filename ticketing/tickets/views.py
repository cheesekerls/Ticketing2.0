from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket, ClaimedTicket
from .print_utils import print_ticket_to_pos as send_to_printer
from django.utils import timezone
from services.models import Service
from escpos.printer import Serial
import qrcode
from io import BytesIO


def print_ticket_to_pos(request, service_id=None):
    message = None  # feedback message

    if request.method == 'POST':
        try:
            # ✅ Get service
            post_service_id = request.POST.get('service_id')
            if post_service_id:
                service = get_object_or_404(Service, pk=int(post_service_id))
            elif service_id is not None:
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
                lane=lane,
                created_at__date=today
            ).order_by('-queue_position').first()

            next_position = (last_ticket.queue_position + 1) if last_ticket else 1

            # ✅ Ticket number with lane prefix (R or P)
            ticket_number = f"{service.service_name[:3].upper()}-{lane[:1]}{next_position:03d}"

            # ✅ Create the ticket
            ticket = Ticket.objects.create(
                ticket_number=ticket_number,
                service=service,
                status="Waiting",
                created_at=timezone.now(),
                lane=lane,
                queue_position=next_position  # NEW: track position in queue
            )

            # ✅ Ticket text
            ticket_text = f"""
             Ticket No: {ticket.ticket_number}
             Service: {ticket.service.service_name}
             Lane: {ticket.lane}
            """

            # ✅ QR Code
            qr = qrcode.make(f"{ticket.ticket_number}")
            qr_io = BytesIO()
            qr.save(qr_io, format="PNG")
            qr_bytes = qr_io.getvalue()

            # ✅ Print
            try:
                send_to_printer(ticket_text, qr_data=ticket.ticket_number)
                message = f" successfully printed!"
            except Exception as e:
                message = f"Ticket created but printing failed: {e}"

        except Exception as e:
            message = f"Error: {e}"

    # Always render page
    services = Service.objects.all()
    return render(request, 'tickets/create_ticket.html', {
        'services': services,
        'message': message
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