# chat/ws/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Извлекаем название комнаты из URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Создаем имя группы для комнаты
        self.room_group_name = f'chat_{self.room_name}'

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Принимаем соединение
        await self.accept()

    async def disconnect(self, close_code):
        # Удаляемся из группы при отключении
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # При получении сообщения из WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    async def chat_message(self, event):
        # Получаем сообщение, отправленное в группу
        message = event['message']
        # Отправляем сообщение обратно клиенту
        await self.send(text_data=json.dumps({
            'message': message
        }))