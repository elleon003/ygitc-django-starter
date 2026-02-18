import os
import requests
from django.conf import settings


def get_client_ip(request) -> str | None:
    """
    Return the client IP for use with Turnstile/rate limiting.
    Only uses X-Forwarded-For when behind a trusted proxy (SECURE_PROXY_SSL_HEADER set).
    """
    if not request:
        return None
    if getattr(settings, 'SECURE_PROXY_SSL_HEADER', None):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR')


def rate_limit_key(group, request):
    """Callable for django-ratelimit key= using proxy-aware client IP."""
    return (get_client_ip(request) or 'unknown')


def verify_turnstile(token: str, remote_ip: str = None) -> bool:
    """
    Verify Cloudflare Turnstile CAPTCHA token
    
    Args:
        token: The Turnstile token from the client
        remote_ip: The user's IP address (optional)
    
    Returns:
        bool: True if verification successful, False otherwise
    """
    secret_key = os.environ.get('TURNSTILE_SECRET_KEY')
    if not secret_key:
        if not getattr(settings, 'DEBUG', True):
            return False  # Production: fail closed when Turnstile not configured
        return True  # Development: skip verification when not configured

    verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    
    data = {
        'secret': secret_key,
        'response': token,
    }
    
    if remote_ip:
        data['remoteip'] = remote_ip
    
    try:
        response = requests.post(verify_url, data=data, timeout=10)
        result = response.json()
        return result.get('success', False)
    except (requests.RequestException, ValueError):
        return False

def get_turnstile_site_key() -> str:
    """Get the Turnstile site key for frontend use"""
    return os.environ.get('TURNSTILE_SITE_KEY', '')

def is_turnstile_enabled() -> bool:
    """Check if Turnstile is properly configured"""
    return bool(get_turnstile_site_key() and os.environ.get('TURNSTILE_SECRET_KEY'))