"""
احراز هویت ساده برای API
"""
from rest_framework import authentication
from django.contrib.sessions.models import Session


class SimpleSessionAuthentication(authentication.SessionAuthentication):
    """احراز هویت بر اساس session"""
    
    def authenticate(self, request):
        # بررسی session
        session_key = request.COOKIES.get('sessionid') or request.META.get('HTTP_AUTHORIZATION')
        
        if not session_key:
            return None
        
        # بررسی session در دیتابیس
        try:
            session = Session.objects.get(session_key=session_key)
            if session.get_decoded().get('authenticated'):
                return (None, None)  # Session معتبر است
        except Session.DoesNotExist:
            pass
        
        return None

