from .base import *

# Development-specific settings
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-#9ncyo)*vy7^*r@b6y34y-k02eieu*x1)pb79)poe6e_m2t^w_')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1],0.0.0.0').split(',')

# Use X-Forwarded-Host header for proper host detection in Docker
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = None  # Not needed for development

# Add development-specific apps
INSTALLED_APPS += [
    'django_browser_reload',
]

# Add development-specific middleware
MIDDLEWARE += [
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security settings - relaxed for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Cache - dummy cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}