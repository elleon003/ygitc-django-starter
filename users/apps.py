from django.apps import AppConfig
import os

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        # Only initialize SuperTokens when not running migrations
        import sys
        if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
            from config.supertokens_config import init_supertokens
            init_supertokens()
