from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast_new_ticket(department_id, ticket_number):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"department_{department_id}",
        {
            "type": "new_ticket",
            "ticket_number": ticket_number,
        }
    )
