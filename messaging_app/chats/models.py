from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.utils import timezone

"""class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation.id}"

    class Meta:
        ordering = ['-timestamp']"""
        
class UserRole(models.TextChoices):
   GUEST = 'guest', 'Guest'
   HOST = 'host', 'Host'
   ADMIN = 'admin', 'Admin'
   
class User(AbstractUser):
    
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        password=True
    )
    
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    
    email = models.EmailField(unique=True, null=False, blank=False)
    
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.GUEST,
        null=False,
        blank=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)  
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'user' 
        indexes = [
            models.Index(fields=['email']),  
            ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
class Conversation(models.Model):

    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    participants = models.ManyToManyField(
        User,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation'
        ordering = ['-created_at']  
    
    def __str__(self):
        participant_names = [str(user) for user in self.participants.all()]
        return f"Conversation between: {', '.join(participant_names)}"
    
class Message(models.Model):
    
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages' 
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    message_body = models.TextField(null=False, blank=False)
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message'
        ordering = ['sent_at']
    
    def __str__(self):
        return f"Message from {self.sender} at {self.sent_at}"
    
