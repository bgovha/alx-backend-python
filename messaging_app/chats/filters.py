import django_filters
from django_filters import rest_framework as filters
from .models import Message, Conversation

class MessageFilter(filters.FilterSet):
    conversation = filters.NumberFilter(field_name='conversation__id')
    participant = filters.NumberFilter(method='filter_by_participant')
    start_date = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    sender = filters.NumberFilter(field_name='sender__id')
    
    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'start_date', 'end_date']
    
    def filter_by_participant(self, queryset, name, value):
        """
        Filter messages by conversation where the specified user is a participant
        """
        return queryset.filter(conversation__participants__id=value)

class ConversationFilter(filters.FilterSet):
    participant = filters.NumberFilter(method='filter_by_participant')
    
    class Meta:
        model = Conversation
        fields = ['participant']
    
    def filter_by_participant(self, queryset, name, value):
        """
        Filter conversations where the specified user is a participant
        """
        return queryset.filter(participants__id=value)