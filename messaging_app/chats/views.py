# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer, ConversationSerializer, MessageSerializer,
    ConversationCreateSerializer, MessageCreateSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Return the conversation with full details
        full_serializer = ConversationSerializer(conversation)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set the sender to the current user (in a real app, this would be the authenticated user)
        # For now, we'll use the first user as a placeholder
        if not User.objects.exists():
            # Create a default user if none exists
            default_user = User.objects.create(
                first_name="Default",
                last_name="User",
                email="default@example.com",
                role="admin"
            )
            default_user.set_password("password")
            default_user.save()
        
        # Use the first available user as sender (in production, use request.user)
        sender = User.objects.first()
        message = serializer.save(sender=sender)
        
        # Return the message with full details
        full_serializer = MessageSerializer(message)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)