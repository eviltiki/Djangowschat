from django.shortcuts import render
from django.views import View
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.chat.models import Chat, Message
from apps.chat.serializers import ChatSerializer, MessageSerializer


# Create your views here.
class ChatViewSet(ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(participant=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        participants_ids = self.request.data.get('participants', [])

        if not participants_ids:
            raise serializers.ValidationError('You must specify at least one participant')

        chat = serializer.save()
        chat.participants.set(participants_ids)

        if not chat.is_group and participants_ids.count() != 2:
            raise serializers.ValidationError('A private chat must have exactly 2 participants')

        chat.save()

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Пользователь может получить историю сообщений конкретного чата.
        Дополнительно можно добавить постраничное разбиение и фильтрацию.
        """
        chat = get_object_or_404(Chat, pk=pk)
        # Проверяем, что текущий пользователь является участником чата
        if request.user not in chat.participants.all():
            return Response({"detail": "Нет доступа к данному чату."}, status=status.HTTP_403_FORBIDDEN)
        messages = chat.messages.order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

#TODO: разобраться с этим вьюсэтом
class MessageViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с сообщениями.
    Здесь пользователи могут создавать сообщения и получать историю сообщений.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Позволяет фильтровать сообщения по чату (ожидается параметр chat_id)
        chat_id = self.request.query_params.get('chat_id')
        if chat_id:
            chat = get_object_or_404(Chat, id=chat_id)

            if self.request.user not in chat.participants.all():
                raise PermissionDenied("Нет доступа к этому чату.")
            return Message.objects.filter(chat__id=chat_id).order_by('created_at')
        return Message.objects.none()

    def perform_create(self, serializer):
        # При создании сообщения устанавливаем текущего пользователя как отправителя
        serializer.save(sender=self.request.user)