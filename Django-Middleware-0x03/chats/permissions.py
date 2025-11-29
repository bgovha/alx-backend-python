from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        if hasattr(obj, 'participants'):
            # For Conversation objects
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            # For Message objects - check if user is in conversation participants
            return request.user in obj.conversation.participants.all()
        elif hasattr(obj, 'sender'):
            # For direct message-like objects
            return request.user == obj.sender or request.user == obj.receiver
        
        return False

class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Permission to only allow owners of an object to "PUT", "PATCH", "DELETE it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to participants
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'participants'):
                return request.user in obj.participants.all()
            elif hasattr(obj, 'conversation'):
                return request.user in obj.conversation.participants.all()
        
        # Write permissions are only allowed to the sender/owner
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
        
        return False