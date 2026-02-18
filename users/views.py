from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from ratelimit.decorators import ratelimit

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .turnstile import get_turnstile_site_key, is_turnstile_enabled, verify_turnstile, get_client_ip
import sesame.utils

User = get_user_model()

# Generic message for magic link to avoid user enumeration
MAGIC_LINK_SENT_MESSAGE = (
    'If an account exists for this email, you will receive a magic link shortly. '
    'Please check your inbox and spam folder.'
)


def _send_magic_link_if_exists(request, email: str) -> None:
    """Send magic link email if user exists; always show same success message."""
    try:
        user = User.objects.get(email=email)
        token = sesame.utils.get_token(user)
        magic_link = request.build_absolute_uri(
            reverse('magic_login', kwargs={'token': token})
        )
        send_mail(
            'Your Magic Login Link',
            f'Click this link to log in: {magic_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        pass
    except Exception:
        pass
    messages.success(request, MAGIC_LINK_SENT_MESSAGE)


@ratelimit(key='users.turnstile.rate_limit_key', rate='5/m', method='POST', block=False)
def register_view(request):
    if getattr(request, 'ratelimit', {}).get('limited'):
        messages.error(request, 'Too many registration attempts. Please try again in a minute.')
        form = CustomUserCreationForm(request=request)
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request=request)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm(request=request)
    context = {
        'form': form,
        'turnstile_site_key': get_turnstile_site_key(),
        'turnstile_enabled': is_turnstile_enabled(),
    }
    return render(request, 'registration/register.html', context)


@ratelimit(key='users.turnstile.rate_limit_key', rate='10/m', method='POST', block=False)
def login_view(request):
    if getattr(request, 'ratelimit', {}).get('limited'):
        messages.error(request, 'Too many login attempts. Please try again in a minute.')
        form = CustomAuthenticationForm()
    elif request.method == 'POST':
        # Check if this is a magic link request
        if 'magic_link' in request.POST:
            email = (request.POST.get('email') or '').strip().lower()
            if not email:
                messages.error(request, 'Please enter your email address.')
            elif is_turnstile_enabled():
                turnstile_token = request.POST.get('cf_turnstile_response_magic')
                if not turnstile_token:
                    messages.error(request, 'Please complete the CAPTCHA verification.')
                elif not verify_turnstile(turnstile_token, get_client_ip(request)):
                    messages.error(request, 'CAPTCHA verification failed. Please try again.')
                else:
                    _send_magic_link_if_exists(request, email)
            else:
                _send_magic_link_if_exists(request, email)
            form = CustomAuthenticationForm()
        else:
            # Regular login form
            form = CustomAuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                return redirect('dashboard')  # Redirect to your dashboard or home page
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()
    context = {
        'form': form,
        'turnstile_site_key': get_turnstile_site_key(),
        'turnstile_enabled': is_turnstile_enabled(),
    }
    return render(request, 'registration/login.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {'user': request.user})

def magic_login_view(request, token):
    """Handle magic link login"""
    user = sesame.utils.get_user(token)
    if user is not None:
        login(request, user)
        messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
        return redirect('dashboard')
    else:
        messages.error(request, 'Invalid or expired magic link.')
        return redirect('login')

@login_required
def user_settings_view(request):
    return render(request, 'user_settings.html', {'user': request.user})
