from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .turnstile import get_turnstile_site_key, is_turnstile_enabled
import os

def register_view(request):
    if request.method == 'POST':
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

def login_view(request):
    if request.method == 'POST':
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

@login_required
def user_settings_view(request):
    return render(request, 'user_settings.html', {'user': request.user})
