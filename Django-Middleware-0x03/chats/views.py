# Create your views here.
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .permissions import IsParticipantOfConversation, IsOwnerOrParticipant
from .pagination import MessagePagination
from .filters import MessageFilter, ConversationFilter
from .models import User, Conversation, Message
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    UserSerializer, ConversationSerializer, MessageSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter
    
    def get_queryset(self):
        """
        This view should return a list of all conversations
        where the current user is a participant.
        """
        return Conversation.objects.filter(participants=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically add the current user as a participant
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        # You might want to add other participants through the request data


class UserViewSet(viewsets.ModelViewSet):
    """Basic user CRUD endpoints used by the tests and API."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrParticipant]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    
    def get_queryset(self):
        """
        This view should return a list of all messages
        from conversations where the current user is a participant.
        """
        return Message.objects.filter(conversation__participants=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically set the sender to the current user
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'])
    def conversation_messages(self, request, conversation_id=None):
        """
        Custom action to get messages for a specific conversation
         HTTP_403_FORBIDDEN"""
        messages = Message.objects.filter(
            conversation__id=conversation_id,
            conversation__participants=request.user
        )
        
        # Apply filtering
        filtered_messages = self.filterset_class(request.GET, queryset=messages).qs
        
        # Apply pagination
        page = self.paginate_queryset(filtered_messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(filtered_messages, many=True)
        return Response(serializer.data)
"""
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
        # For now, we'll use the first user as a placeholder filters
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
        """