from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Conversation, Message, UserRole


class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password] 
    )
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name', 
            'last_name',
            'full_name',
            'password',
            'phone_number',
            'role',
            'created_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True}, 
            'user_id': {'read_only': True},   
        }
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def create(self, validated_data):
    
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)  # This hashes the password
        user.save()
        return user
    
    def update(self, instance, validated_data):
        
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
       
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserSummarySerializer(serializers.ModelSerializer):
 
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'full_name', 'role']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    
class MessageSerializer(serializers.ModelSerializer):
  
    sender = UserSummarySerializer(read_only=True)
    
    sender_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',       
            'sender_id',    
            'conversation',  
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'sender']
    
    def validate_sender_id(self, value):

        try:
            user = User.objects.get(user_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        
        conversation_id = self.initial_data.get('conversation')
        if conversation_id:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                if not conversation.participants.filter(user_id=value).exists():
                    raise serializers.ValidationError("User is not a participant in this conversation")
            except Conversation.DoesNotExist:
                raise serializers.ValidationError("Conversation does not exist")
        
        return value
    
    def create(self, validated_data):
       
        sender_id = validated_data.pop('sender_id')
        sender = User.objects.get(user_id=sender_id)
        
        message = Message.objects.create(
            sender=sender,
            **validated_data
        )
        return message
    
    
class ConversationSerializer(serializers.ModelSerializer):
   
    participants = UserSummarySerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
   
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )
    
    participant_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',       
            'participant_ids',    
            'messages',           
            'participant_count',
            'last_message',
            'last_message_time',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        return last_message.message_body if last_message else None
    
    def get_last_message_time(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        return last_message.sent_at if last_message else None
    
    def validate_participant_ids(self, value):
       
        if len(value) < 2:
            raise serializers.ValidationError("Conversation must have at least 2 participants")
     
        existing_users = User.objects.filter(user_id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("One or more users do not exist")
        
        return value
    
    def create(self, validated_data):
       
        participant_ids = validated_data.pop('participant_ids')
       
        conversation = Conversation.objects.create()
        
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.set(participants)
        
        return conversation
    
    def update(self, instance, validated_data):
      
        participant_ids = validated_data.pop('participant_ids', None)
        
        if participant_ids is not None:
            participants = User.objects.filter(user_id__in=participant_ids)
            instance.participants.set(participants)
        
        instance.save()
        return instance


class ConversationSummarySerializer(serializers.ModelSerializer):
   
    participants = UserSummarySerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_count',
            'last_message_preview',
            'created_at'
        ]
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_last_message_preview(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            # Return first 50 characters of last message
            preview = last_message.message_body[:50]
            if len(last_message.message_body) > 50:
                preview += '...'
            return preview
        return None
    
    """from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'participant_ids', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        # Add participants
        current_user = self.context['request'].user
        conversation.participants.add(current_user)
        
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                conversation.participants.add(user)
            except User.DoesNotExist:
                pass
        
        return conversation"""