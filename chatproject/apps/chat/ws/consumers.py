# chat/ws/consumers.py
import json
from tokenize import group

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied

from apps.chat.models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close(code=4001)
            return

        self.user_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        # Принимаем соединение
        await self.accept()

        chats = await self.get_user_chats()
        await self.send(text_data=json.dumps({
            "type": "chat_list",
            "chats": chats,
        }))

    async def disconnect(self, close_code):
        # Удаляемся из группы при отключении
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            event_type = data.get("type")

            if event_type == "send_message":
                await self.handle_send_message(data)
            # elif event_type == "typing":
            #     await self.handle_typing(data)
            else:
                await self.send(text_data=json.dumps({"error": "Unknown event type"}))

    async def handle_send_message(self, data):
        chat_id = data.get("chat_id")
        message_text = data.get("message")
        if not chat_id or not message_text:
            await self.send(text_data=json.dumps({"error": "chat_id and message are required"}))

        message = await self.save_message(chat_id, message_text)
        if message is None:
            await self.send(text_data=json.dumps({"error": "message not found"}))
            return

        participants = await self.get_chat_participants(chat_id)

        payload = {
            "type": "send_message",
            "chat_id": chat_id,
            "message": {
                "id": message.id,
                "sender": message.sender.username,
                "content": message.content,
                "created_at": str(message.created_at),
            }
        }

        for participant_id in participants:
            if participant_id != self.user.id:
                group_name = f"user_{participant_id}"
                await self.channel_layer.group_send(group_name, {
                    "type": "chat.message",
                    "payload": payload,
                })

    async def chat_message(self, event):
        payload = event["payload"]
        await self.send(text_data=json.dumps(payload))

    @database_sync_to_async
    def save_message(self, chat_id, message_text):
        try:
            chat = Chat.objects.get(pk=chat_id)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("Чат с указанным идентификатором не найден.")

        # Проверка, что пользователь является участником чата.
        if not chat.participants.filter(pk=self.user.id).exists():
            raise PermissionDenied("Пользователь не состоит в этом чате.")

        message = Message.objects.create(
            chat=chat,
            sender=self.user,
            content=message_text
        )
        return message

    @database_sync_to_async
    def get_chat_participants(self, chat_id):
        try:
            chat = Chat.objects.get(pk=chat_id)
            return list(chat.participants.values_list('id', flat=True))
        except ObjectDoesNotExist:
            return []

    @database_sync_to_async
    def get_user_chats(self):
        chats = Chat.objects.filter(participants=self.user).values("id", "name")
        return list(chats)