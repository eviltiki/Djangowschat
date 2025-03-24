from django.contrib.auth.models import User
from rest_framework import serializers

from apps.chat.models import Message, Chat


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']

class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'name', 'is_group', 'participants', 'created_at', 'last_message']
        read_only_fields = ['id', 'created_at', 'last_message']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()

        if last_message:
            return MessageSerializer(last_message).data
        return None