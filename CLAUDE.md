# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready Django starter template with modern authentication, Tailwind CSS styling, and social authentication capabilities. It uses Django Social Auth (replacing SuperTokens) with a custom email-based user model and includes Cloudflare Turnstile CAPTCHA protection.

## Development Commands

### Local Development Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tailwind dependencies
python manage.py tailwind install

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Recommended: Run both Django and Tailwind in one command
python manage.py tailwind dev

# Alternative: Run separately in different terminals
python manage.py runserver
python manage.py tailwind start
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Frontend Development
```bash
# Install Tailwind dependencies
python manage.py tailwind install

# Start Tailwind watcher (development)
python manage.py tailwind start

# Build for production
python manage.py tailwind build
```

### Docker Development
```bash
# Basic setup (Django + PostgreSQL + Redis)
docker compose up --build

# With Tailwind development (recommended for frontend work)
docker compose --profile dev up --build

# Run migrations in Docker
docker compose exec web python manage.py migrate

# Create superuser in Docker
docker compose exec web python manage.py createsuperuser

# View logs
docker compose logs -f web
```

**Docker Services:**
- **db**: PostgreSQL 15 with health checks
- **redis**: Redis 7-alpine for caching
- **web**: Django application (Python 3.12 + Node.js build)
- **tailwind**: CSS compilation (dev profile only)

## Architecture

### Settings Structure
- **Split settings architecture**: `config/settings/base.py`, `development.py`, `production.py`
- **Environment-based configuration**: Uses environment variables with sensible defaults
- **Development vs Production**: Automatic security settings based on environment

### Authentication System
- **Custom User Model**: `users.CustomUser` with email as primary identifier
- **Social Authentication**: Django Social Auth with Google and LinkedIn OAuth2 support
- **CAPTCHA Protection**: Cloudflare Turnstile integration for forms
- **Session-based**: Uses Django's built-in session authentication

### Frontend Stack
- **Tailwind CSS 4.x**: Utility-first CSS framework
- **DaisyUI 5.x**: Component library built on Tailwind
- **django-tailwind**: Integration with live reload
- **PostCSS**: CSS processing with plugins

### Database Configuration
- **Development**: SQLite (default)
- **Production**: PostgreSQL support with environment variables
- **Docker**: PostgreSQL 15 container with health checks and Redis 7-alpine

## Key Apps and Models

### Users App (`users/`)
- **CustomUser**: Email-based authentication model (users/models.py:32)
- **CustomUserManager**: Manager for email-based user creation (users/models.py:5)
- **Authentication views**: Register, login, logout, dashboard, settings (users/views.py)

### Theme App (`theme/`)
- **Template organization**: Base templates with partials system
- **Static file handling**: Tailwind compilation and distribution
- **Component templates**: Reusable UI components in partials/

### URL Structure
- `/`: Home page
- `/users/register/`: User registration
- `/users/login/`: User login
- `/users/logout/`: User logout
- `/users/dashboard/`: User dashboard (login required)
- `/users/settings/`: User settings (login required)
- `/admin/`: Django admin panel

## Environment Configuration

### Required Environment Variables
```bash
SECRET_KEY=your-secret-key
DEBUG=True  # False for production
DJANGO_SETTINGS_MODULE=config.settings.development
```

### Optional Environment Variables
```bash
# Database (defaults to SQLite)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=database_name
DB_USER=database_user
DB_PASSWORD=database_password
DB_HOST=localhost
DB_PORT=5432

# Django Social Auth - OAuth Provider Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Turnstile CAPTCHA
TURNSTILE_SITE_KEY=your-turnstile-site-key
TURNSTILE_SECRET_KEY=your-turnstile-secret-key

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## Development Workflows

### Adding New Features
1. Create Django app: `python manage.py startapp myapp`
2. Add to `INSTALLED_APPS` in `config/settings/base.py`
3. Create models and run migrations
4. Add templates to `theme/templates/`
5. Configure URLs in app and include in `config/urls.py`

### Styling and Templates
1. Edit CSS in `theme/static_src/src/styles.css`
2. Templates extend `base.html` with `{% extends 'base.html' %}`
3. Use DaisyUI components and Tailwind utilities
4. Partials in `theme/templates/partials/` for reusable components

### Social Authentication Setup
1. Configure OAuth providers (Google, LinkedIn)
2. Set environment variables for client credentials
3. Authentication backends configured in `base.py` (line 123-127)
4. URLs included via `social_django.urls` (config/urls.py:11)
5. Google: `/complete/google-oauth2/` callback URL
6. LinkedIn: `/complete/linkedin-oauth2/` callback URL

### Testing Locally
- Use test Turnstile keys for development:
  - Site Key: `1x00000000000000000000AA`
  - Secret Key: `1x0000000000000000000000000000000AA`

## Important Files and Locations

- **Main configuration**: `config/settings/base.py`
- **User model**: `users/models.py`
- **URL routing**: `config/urls.py`, `users/urls.py`
- **Templates**: `theme/templates/`
- **Static files**: `theme/static_src/`
- **Tailwind config**: `theme/static_src/tailwind.config.js`
- **Package deps**: `requirements.txt`, `theme/static_src/package.json`

## Production Deployment

### Required Steps
```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=config.settings.production

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic

# Build CSS
python manage.py tailwind build

# Run migrations
python manage.py migrate
```

### Security Notes
- Production settings automatically enable SSL redirects and secure cookies
- Custom user model requires proper email validation
- CAPTCHA protection recommended for production forms
- Social auth requires proper OAuth callback URLs