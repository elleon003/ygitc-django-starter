# Django Starter

A modern, production-ready Django starter template with authentication, beautiful UI, and best practices built-in.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Settings Architecture](#settings-architecture)
- [User Authentication](#user-authentication)
  - [Custom User Model](#custom-user-model)
  - [Available Views](#available-views)
- [Social Authentication Setup](#social-authentication-setup)
  - [SuperTokens Configuration](#supertokens-configuration)
  - [Cloudflare Turnstile Setup](#cloudflare-turnstile-setup)
- [Authentication Features](#authentication-features)
  - [Traditional Email/Password Authentication](#traditional-emailpassword-authentication)
  - [Social Authentication Options](#social-authentication-options)
  - [CAPTCHA Protection](#captcha-protection)
- [Frontend Development](#frontend-development)
  - [Tailwind CSS](#tailwind-css)
  - [Development Workflow](#development-workflow)
  - [Template System](#template-system)
- [Deployment](#deployment)
  - [Production Checklist](#production-checklist)
  - [Docker Deployment](#docker-deployment)
- [Development](#development)
  - [Adding New Features](#adding-new-features)
  - [Customizing Styles](#customizing-styles)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- 🚀 **Fast Setup**: Pre-configured authentication and user management
- 🎨 **Beautiful UI**: Built with Tailwind CSS and DaisyUI components
- 🔒 **Secure**: Production-ready security settings and best practices
- 📱 **Responsive**: Mobile-first design with modern CSS framework
- ⚙️ **Flexible Configuration**: Separate development and production settings
- 🔐 **Custom User Model**: Email-based authentication instead of username
- 🌐 **Social Authentication**: Google, LinkedIn, and Magic Link login via SuperTokens
- 🤖 **CAPTCHA Protection**: Cloudflare Turnstile integration for bot protection
- 🎯 **Ready to Deploy**: Environment-based configuration system

## Tech Stack

- **Backend**: Django 5.2.5
- **Frontend**: Tailwind CSS 4.x, DaisyUI 5.x
- **Authentication**: Custom User model with email-based login + SuperTokens for social auth
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Styling**: django-tailwind with live reload
- **Development**: django-browser-reload for hot reloading
- **Security**: Cloudflare Turnstile CAPTCHA protection
- **Social Auth**: Google, LinkedIn OAuth + Magic Link authentication

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js and npm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ygitc-django-starter
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tailwind dependencies**
   ```bash
   python manage.py tailwind install
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env.dev
   # Edit .env.dev with your settings
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server**

   Run both Django and Tailwind watcher with a single command:
   ```bash
   python manage.py tailwind dev
   ```

   Or run them separately in different terminals:
   ```bash
   # Terminal 1 - Django
   python manage.py runserver
   
   # Terminal 2 - Tailwind watcher
   python manage.py tailwind start
   ```

9. **Visit the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
ygitc-django-starter/
├── config/                 # Project configuration
│   ├── settings/           # Split settings (base, development, production)
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/                  # Custom user authentication app
│   ├── models.py          # Custom user model
│   ├── forms.py           # Registration and login forms
│   ├── views.py           # Authentication views
│   └── urls.py
├── theme/                  # UI theme and templates
│   ├── templates/         # HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── partials/      # Reusable template components
│   │   └── registration/  # Auth templates
│   ├── static/            # Compiled CSS
│   └── static_src/        # Tailwind source files
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
├── .env.example          # Environment variables template
└── README.md
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env.dev` for development or `.env` for production and configure:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True  # False for production
DJANGO_SETTINGS_MODULE=config.settings.development  # or production

# Database (optional, defaults to SQLite)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Other settings
TIME_ZONE=America/New_York
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# SuperTokens Configuration
SUPERTOKENS_CONNECTION_URI=https://try.supertokens.com
SUPERTOKENS_API_KEY=your-supertokens-api-key
SUPERTOKENS_APP_NAME=Django Starter
SUPERTOKENS_API_DOMAIN=https://yourdomain.com
SUPERTOKENS_WEBSITE_DOMAIN=https://yourdomain.com

# OAuth Provider Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# Cloudflare Turnstile Configuration
TURNSTILE_SITE_KEY=your-turnstile-site-key
TURNSTILE_SECRET_KEY=your-turnstile-secret-key
```

### Settings Architecture

The project uses a split settings architecture:

- `config/settings/base.py`: Common settings for all environments
- `config/settings/development.py`: Development-specific settings
- `config/settings/production.py`: Production-specific settings

## User Authentication

### Custom User Model

The project uses a custom user model (`users.CustomUser`) with email-based authentication:

- **Email**: Primary identifier (instead of username)
- **First Name**: Optional
- **Last Name**: Optional
- **Password**: Standard Django password validation

### Available Views

- `/users/register/`: User registration
- `/users/login/`: User login
- `/users/logout/`: User logout
- `/users/dashboard/`: User dashboard (login required)
- `/users/settings/`: User settings (login required)

## Social Authentication Setup

### SuperTokens Configuration

This project integrates with SuperTokens for social authentication providers and magic link functionality.

#### 1. Create SuperTokens Account

1. Visit [SuperTokens](https://supertokens.com/) and create an account
2. Create a new application
3. Note down your `Connection URI` and `API Key`

#### 2. Configure OAuth Providers

**Google OAuth Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add your domain to authorized origins
6. Add `http://localhost:8000/auth/callback/google` to authorized redirect URIs

**LinkedIn OAuth Setup:**
1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create a new application
3. Add OAuth 2.0 redirect URLs: `http://localhost:8000/auth/callback/linkedin`
4. Note down Client ID and Client Secret

#### 3. Configure Environment Variables

Add these to your `.env.dev` (development) or `.env` (production):

```bash
# SuperTokens Configuration
SUPERTOKENS_CONNECTION_URI=https://try.supertokens.com
SUPERTOKENS_API_KEY=your-actual-api-key
SUPERTOKENS_APP_NAME=Your App Name
SUPERTOKENS_API_DOMAIN=http://localhost:8000  # or your production domain
SUPERTOKENS_WEBSITE_DOMAIN=http://localhost:8000  # or your production domain

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
```

### Cloudflare Turnstile Setup

Turnstile provides CAPTCHA protection for your forms.

#### 1. Get Turnstile Keys

1. Visit [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Go to Turnstile section
3. Create a new site
4. Add your domain (use `localhost` for development)
5. Choose "Managed" challenge type
6. Copy the Site Key and Secret Key

#### 2. Configure Environment Variables

```bash
# Cloudflare Turnstile
TURNSTILE_SITE_KEY=your-turnstile-site-key
TURNSTILE_SECRET_KEY=your-turnstile-secret-key
```

#### 3. Testing Turnstile

For development/testing, you can use these test keys:
- **Site Key**: `1x00000000000000000000AA`
- **Secret Key**: `1x0000000000000000000000000000000AA`

## Authentication Features

### Traditional Email/Password Authentication
- Email-based user registration and login
- Password validation and security
- Integrated with Turnstile CAPTCHA (when configured)

### Social Authentication Options
- **Google**: One-click login with Google account
- **LinkedIn**: Professional network authentication
- **Magic Link**: Passwordless email-based authentication

### CAPTCHA Protection
- Cloudflare Turnstile integration
- Protects registration and login forms
- Gracefully degrades when not configured

## Frontend Development

### Tailwind CSS

The project uses django-tailwind with DaisyUI components:

- **Tailwind CSS 4.x**: Utility-first CSS framework
- **DaisyUI 5.x**: Component library built on Tailwind
- **PostCSS**: CSS processing with plugins

### Development Workflow

1. **Start development server**: `python manage.py tailwind dev` (runs both Django and Tailwind)
2. **Make style changes**: Edit files in `theme/static_src/src/`
3. **Build for production**: `python manage.py tailwind build`

### Template System

Templates are organized in `theme/templates/`:

- `base.html`: Main layout template
- `partials/`: Reusable components (header, footer)
- `registration/`: Authentication-related templates
- `examples/`: Template examples with different layouts

## Deployment

### Production Checklist

1. **Environment Setup**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.production
   ```

2. **Security Settings** (automatically enabled in production)
   - `DEBUG=False`
   - `SECURE_SSL_REDIRECT=True`
   - `SESSION_COOKIE_SECURE=True`
   - `CSRF_COOKIE_SECURE=True`

3. **Database Migration**
   ```bash
   python manage.py migrate
   ```

4. **Static Files Collection**
   ```bash
   python manage.py collectstatic
   ```

5. **CSS Build**
   ```bash
   python manage.py tailwind build
   ```

### Docker Deployment

The project includes a complete Docker setup for production-like development and deployment.

#### Quick Start with Docker

**Basic setup** (Django + PostgreSQL + Redis):
```bash
docker compose up --build
```

**With Tailwind development** (recommended for frontend work):
```bash
docker compose --profile dev up --build
```

**With self-hosted SuperTokens** (full production simulation):
```bash
docker compose --profile self-hosted up --build
```

**All services**:
```bash
docker compose --profile dev --profile self-hosted up --build
```

#### Docker Services

- **PostgreSQL**: Production-like database instead of SQLite
- **Redis**: Caching and session storage
- **Django Web**: Main application server
- **Tailwind** (dev profile): CSS compilation with live reload
- **SuperTokens Core** (self-hosted profile): Self-hosted authentication service

#### Docker Configuration

The Docker setup uses these files:

- `docker-compose.yml`: Main orchestration configuration
- `Dockerfile`: Multi-stage Python 3.12 + Node.js build
- `.env.docker.example`: Template for Docker environment variables
- `.env.docker`: Your local Docker environment (created from template, git-ignored)
- `.dockerignore`: Optimized build context

#### Environment Variables for Docker

1. **Create your local Docker environment file**:
   ```bash
   cp .env.docker.example .env.docker
   ```

2. **Configure your OAuth and Turnstile keys** in `.env.docker`:
   ```bash
   # OAuth Provider Configuration
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   LINKEDIN_CLIENT_ID=your-linkedin-client-id
   LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

   # Cloudflare Turnstile Configuration
   TURNSTILE_SITE_KEY=your-turnstile-site-key
   TURNSTILE_SECRET_KEY=your-turnstile-secret-key
   ```

> **Security Note**: The `.env.docker` file is automatically ignored by git to prevent committing sensitive credentials.

#### Docker Development Workflow

1. **First-time setup**:
   ```bash
   # Copy and configure environment
   cp .env.docker.example .env.docker
   # Edit .env.docker with your actual OAuth/Turnstile keys
   
   # Start development environment
   docker compose --profile dev up --build
   ```

2. **Run migrations**:
   ```bash
   docker compose exec web python manage.py migrate
   ```

3. **Create superuser**:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

4. **Access the application**:
   - Main app: http://localhost:8000
   - SuperTokens dashboard: http://localhost:3567/auth/dashboard (if using self-hosted profile)

#### Production Docker Deployment

For production, create a production-specific compose file or override the environment variables:

```bash
# Use production environment variables
export DJANGO_SETTINGS_MODULE=config.settings.production
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Deploy with production configuration
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### Docker Profiles Explained

- **Default**: Core services (web, db, redis) - minimal setup
- **dev**: Adds Tailwind compilation for frontend development
- **self-hosted**: Adds SuperTokens Core for testing social auth locally

## Development

### Adding New Features

1. **Create Django apps**: `python manage.py startapp myapp`
2. **Add to INSTALLED_APPS** in `config/settings/base.py`
3. **Create templates** in `theme/templates/`
4. **Add URLs** to `config/urls.py`

### Customizing Styles

1. **Edit Tailwind config**: Modify `theme/static_src/tailwind.config.js`
2. **Add custom CSS**: Edit `theme/static_src/src/styles.css`
3. **Use DaisyUI components**: Available themes and components

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: Report bugs and request features via GitHub issues
- **Documentation**: Check the Django and Tailwind CSS documentation
- **Community**: Join Django and Tailwind CSS communities for support

---

**Built with ❤️ using Django, Tailwind CSS, and modern web development practices.**