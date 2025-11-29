import datetime
import logging
from django.http import HttpResponseForbidden, JsonResponse
from collections import defaultdict
import time
from django.contrib.auth.models import User


logger = logging.getLogger('request_logger')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Log before processing the request
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.datetime.now()} - User: {user} - Path: {request.path}"
        
        # Log to file
        logger.info(log_message)
        
        # Also write to a specific log file
        with open('requests.log', 'a') as f:
            f.write(log_message + '\n')
        
        response = self.get_response(request)
        return response
    
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        current_time = datetime.datetime.now().time()
        start_time = datetime.time(21, 0)  # 9 PM
        end_time = datetime.time(6, 0)     # 6 AM
        
        # Check if current time is between 9 PM and 6 AM
        if (current_time >= start_time or current_time <= end_time):
            # Check if the request is for chat-related paths
            if request.path.startswith('/chat') or '/message' in request.path:
                return HttpResponseForbidden(
                    "Chat access is restricted between 9 PM and 6 AM"
                )
        
        response = self.get_response(request)
        return response
    
class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.offensive_words = ['badword1', 'badword2', 'spam']  # Add offensive words
        self.message_count = defaultdict(list)
        self.limit = 5  # 5 messages per minute
        self.window = 60  # 1 minute in seconds
        
    def __call__(self, request):
        # Rate limiting logic
        if request.method == 'POST' and ('message' in request.path or 'chat' in request.path):
            ip_address = self.get_client_ip(request)
            current_time = time.time()
            
            # Clean old messages outside the time window
            self.message_count[ip_address] = [
                timestamp for timestamp in self.message_count[ip_address]
                if current_time - timestamp < self.window
            ]
            
            # Check if user exceeded the limit
            if len(self.message_count[ip_address]) >= self.limit:
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please wait before sending more messages.'
                }, status=429)
            
            # Add current request timestamp
            self.message_count[ip_address].append(current_time)
            
            # Offensive language detection
            if request.method == 'POST':
                # Check POST data for offensive language
                message_content = ""
                if request.content_type == 'application/json':
                    try:
                        import json
                        data = json.loads(request.body)
                        message_content = data.get('content', '') or data.get('message', '')
                    except:
                        pass
                elif request.POST:
                    message_content = request.POST.get('content', '') or request.POST.get('message', '')
                
                # Check for offensive words
                if any(word in message_content.lower() for word in self.offensive_words):
                    return JsonResponse({
                        'error': 'Message contains offensive language and cannot be sent.'
                    }, status=400)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.restricted_paths = ['/admin/chat/', '/api/admin/', '/moderate/']
        
    def __call__(self, request):
        # Check if the path requires admin/moderator permissions
        if any(path in request.path for path in self.restricted_paths):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")
            
            # Check if user has admin or moderator role
            # Assuming you have a UserProfile model with role field
            # Or using Django's built-in is_staff for admin
            if not (request.user.is_staff or self.is_moderator(request.user)):
                return HttpResponseForbidden("Insufficient permissions. Admin or moderator role required.")
        
        response = self.get_response(request)
        return response
    
    def is_moderator(self, user):
        # Implement your moderator check logic here
        # This could check a user profile model or groups
        try:
            return user.profile.role in ['admin', 'moderator']
        except:
            return False