# Django Starter

A modern, production-ready Django starter template with authentication, beautiful UI, and best practices built-in.

## Features

- 🚀 **Fast Setup**: Pre-configured authentication and user management
- 🎨 **Beautiful UI**: Built with Tailwind CSS and DaisyUI components
- 🔒 **Secure**: Production-ready security settings and best practices
- 📱 **Responsive**: Mobile-first design with modern CSS framework
- ⚙️ **Flexible Configuration**: Separate development and production settings
- 🔐 **Custom User Model**: Email-based authentication instead of username
- 🎯 **Ready to Deploy**: Environment-based configuration system

## Tech Stack

- **Backend**: Django 5.2.5
- **Frontend**: Tailwind CSS 4.x, DaisyUI 5.x
- **Authentication**: Custom User model with email-based login
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Styling**: django-tailwind with live reload
- **Development**: django-browser-reload for hot reloading

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
   cd theme/static_src
   npm install
   cd ../..
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

8. **Start the development servers**

   In one terminal (Django):
   ```bash
   python manage.py runserver
   ```

   In another terminal (Tailwind):
   ```bash
   python manage.py tailwind start
   ```

   Or use the Procfile with foreman/honcho:
   ```bash
   foreman start -f Procfile.tailwind
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

## Frontend Development

### Tailwind CSS

The project uses django-tailwind with DaisyUI components:

- **Tailwind CSS 4.x**: Utility-first CSS framework
- **DaisyUI 5.x**: Component library built on Tailwind
- **PostCSS**: CSS processing with plugins

### Development Workflow

1. **Start Tailwind compiler**: `python manage.py tailwind start`
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

The project is ready for Docker deployment with proper environment variable support.

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