from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Chat(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, help_text="The name of the chat")
    is_group = models.BooleanField(default=False, help_text="Whether this chat belongs to a group")
    participants = models.ManyToManyField(User, related_name="chat_participants")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_group:
            return f"Group chat {self.name}"

        participants = self.participants.all()

        if participants.count() == 2:
            return f"Personal chat: {self.name} {participants[0].username} and {participants[1].username}"
        return f"Personal chat"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField(help_text="The message content")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message sent by {self.sender} to {self.chat} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
