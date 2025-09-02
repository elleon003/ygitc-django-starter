from django.apps import AppConfig

class UsersConfigWithSupertokens(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        # Initialize SuperTokens when app is ready
        from config.supertokens_config import init_supertokens
        init_supertokens()