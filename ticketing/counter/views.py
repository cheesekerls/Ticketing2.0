from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from tickets.models import Ticket
from django.db import transaction
from django.http import JsonResponse

def queue_dashboard(request):
    # Ensure all tickets have a queue_position (fallback if older ones don't)
    for idx, t in enumerate(Ticket.objects.filter(status__in=['Waiting', 'Skipped']).order_by('created_at'), start=1):
        if not t.queue_position:
            t.queue_position = idx
            t.save()

    tickets = Ticket.objects.filter(status__in=['Waiting', 'Skipped']).order_by('queue_position')
    current_ticket = Ticket.objects.filter(status='Called').last()

    return render(request, 'counter/dashboard.html', {
        'tickets': tickets,
        'current_ticket': current_ticket
    })



from django.shortcuts import redirect
from django.db import transaction
from tickets.models import Ticket

def call_next_ticket(request):
    """
    Alternates between Priority and Regular queues.
    If one lane is empty, continues with the other.
    Works with Ticket model that uses ticket_id as primary key.
    """

    with transaction.atomic():
        # Mark any currently called tickets as served
        Ticket.objects.filter(status='Called').update(status='Served')

        # Get the most recently served or called ticket
        last_ticket = Ticket.objects.filter(status__in=['Served', 'Called']).order_by('-ticket_id').first()

        # Determine preferred lane
        if last_ticket:
            last_lane = (last_ticket.lane or '').strip()
            if last_lane.lower() == 'priority':
                preferred_lane = 'Regular'
            else:
                preferred_lane = 'Priority'
        else:
            preferred_lane = 'Priority'  # Default start

        print(f"[call_next_ticket] last_ticket={getattr(last_ticket,'ticket_number',None)} lane={getattr(last_ticket,'lane',None)} next_preferred={preferred_lane}")

        # Helper function
        def get_next_waiting(lane):
            return (
                Ticket.objects
                .filter(lane__iexact=lane, status='Waiting')
                .order_by('queue_position', 'created_at', 'ticket_id')
                .select_for_update(skip_locked=True)
                .first()
            )

        # Try preferred lane
        next_ticket = get_next_waiting(preferred_lane)

        # If none found, fallback to other lane
        if not next_ticket:
            fallback = 'Priority' if preferred_lane == 'Regular' else 'Regular'
            next_ticket = get_next_waiting(fallback)
            print(f"[call_next_ticket] fallback to {fallback}")

        # If still none, try skipped
        if not next_ticket:
            next_ticket = (
                Ticket.objects
                .filter(status='Skipped')
                .order_by('queue_position', 'created_at', 'ticket_id')
                .select_for_update(skip_locked=True)
                .first()
            )
            if next_ticket:
                print("[call_next_ticket] using skipped ticket")

        # Call the ticket if found
        if next_ticket:
            next_ticket.status = 'Called'
            next_ticket.save()
            print(f"[call_next_ticket] calling {next_ticket.ticket_number} ({next_ticket.lane})")
        else:
            print("[call_next_ticket] no available ticket to call")

    return redirect('queue_dashboard')




def skip_ticket(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    # Find the next ticket immediately after this one
    next_ticket = Ticket.objects.filter(
        queue_position__gt=ticket.queue_position,
        status__in=['Waiting', 'Skipped']
    ).order_by('queue_position').first()

    if next_ticket:
        # Swap their positions
        current_pos = ticket.queue_position
        ticket.queue_position = next_ticket.queue_position
        next_ticket.queue_position = current_pos

        # Mark as skipped
        ticket.status = 'Skipped'

        ticket.save()
        next_ticket.save()
    else:
        # If it's already last, just mark skipped
        ticket.status = 'Skipped'
        ticket.save()

    return redirect('queue_dashboard')





def cancel_ticket(request, ticket_number):
    if request.method == 'POST':
        try:
            ticket = Ticket.objects.get(ticket_number=ticket_number)
            ticket.status = 'Cancelled'
            ticket.save()
            return JsonResponse({'success': True})
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})