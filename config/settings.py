import os
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()

# Determine which settings module to use
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if settings_module == 'config.settings.development':
    from .settings.development import *
elif settings_module == 'config.settings.production':
    from .settings.production import *
else:
    from .settings.development import *   
