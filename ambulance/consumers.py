import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage, EmergencyRequest, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["request_id"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        history = await self.get_message_history(self.room_name)
        await self.send(text_data=json.dumps({
            "type": "history",
            "messages": history
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        user = self.scope["user"]
        if not user.is_authenticated:
            return  # Optionally, send an error message

        msg = await self.save_message(self.room_name, user.id, message)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"]
        }))

    @database_sync_to_async
    def get_message_history(self, room_name):
        msgs = ChatMessage.objects.filter(request_id=room_name).order_by("timestamp")
        return [
            {
                "id": m.id,
                "message": m.message,
                "sender": m.user.firstname if hasattr(m.user, "firstname") else str(m.user),
                "sender_id": m.user.id,
                "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M"),
            }
            for m in msgs
        ]

    @database_sync_to_async
    def save_message(self, room_name, sender_id, message):
        user = User.objects.get(id=sender_id)
        req = EmergencyRequest.objects.get(id=room_name)
        msg = ChatMessage.objects.create(request=req, user=user, message=message)
        return {
            "id": msg.id,
            "message": msg.message,
            "sender": user.firstname if hasattr(user, "firstname") else str(user),
            "sender_id": user.id,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
        }
