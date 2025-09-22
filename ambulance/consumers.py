import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.request_id = self.scope['url_route']['kwargs']['request_id']
        self.room_group_name = f'chat_{self.request_id}'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Resolve session user from custom User model
        self.user = await self.get_session_user()

        await self.accept()

        # ✅ Get chat history using async wrapper
        messages = await self.get_messages()
        history = []
        for m in messages:
            is_admin = bool(getattr(m.sender, 'is_admin', False))
            sender_name = "Admin" if is_admin else f"{getattr(m.sender, 'firstname', '')} {getattr(m.sender, 'lastname', '')}".strip()
            history.append({
                "message": m.message,
                "sender": sender_name or "User",
                "sender_id": getattr(m.sender, 'id', None) or getattr(m.sender, 'userid', None),
                "is_admin": is_admin,
                "timestamp": m.timestamp.strftime("%H:%M"),
            })

        # Send history to client
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
        sender = self.user  # custom session-based user

        # ✅ Save message async (only if we have a valid user)
        msg = await self.save_message(sender, message)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "message": msg.message,
                    "sender": ("Admin" if bool(getattr(sender, 'is_admin', False)) else (f"{getattr(sender, 'firstname', '')} {getattr(sender, 'lastname', '')}".strip() or "User")),
                    "sender_id": getattr(sender, 'id', None) or getattr(sender, 'userid', None),
                    "is_admin": bool(getattr(sender, 'is_admin', False)),
                    "timestamp": msg.timestamp.strftime("%H:%M"),
                }
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
        }))

    # -----------------
    # ORM Helpers
    # -----------------
    @database_sync_to_async
    def get_messages(self):
        from .models import ChatMessage
        # Return a concrete list to avoid lazy evaluation in async context
        return list(
            ChatMessage.objects
            .filter(request_id=self.request_id)
            .select_related("sender")
            .order_by("timestamp")[:50]
        )

    @database_sync_to_async
    def save_message(self, sender, message):
        from .models import ChatMessage
        # Guard: if no valid sender from session, we can either reject or save with null
        if sender is None:
            # Optionally, you could raise an exception or skip saving
            return ChatMessage.objects.create(
                request_id=self.request_id,
                sender=None,  # will error if FK not nullable; in that case, require login
                message=message
            )
        return ChatMessage.objects.create(
            request_id=self.request_id,
            sender=sender,
            message=message
        )

    @database_sync_to_async
    def get_session_user(self):
        """Fetch the custom User instance using session 'user_id'."""
        try:
            from .models import User
            session = self.scope.get("session")
            if not session:
                return None
            user_id = session.get("user_id")
            if not user_id:
                return None
            return User.objects.get(pk=user_id)
        except Exception:
            return None
