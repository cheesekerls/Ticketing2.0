from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TVConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # department id from URL route /ws/tv/<department_id>/
        self.department_id = self.scope['url_route']['kwargs']['department_id']
        self.group_name = f"department_{self.department_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def new_ticket(self, event):
        await self.send(text_data=json.dumps({
            'ticket_number': event.get('ticket_number')
        }))
