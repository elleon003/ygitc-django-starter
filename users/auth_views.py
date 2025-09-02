import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .auth_models import AuthProvider, AuthLinkingToken
from .supertokens_auth import MultiAuthHandler
import requests
import os

@login_required
def auth_settings_view(request):
    """Display user's linked authentication methods"""
    auth_providers = AuthProvider.objects.filter(user=request.user)
    
    # Check which providers are available
    available_providers = {
        'email': True,
        'google': bool(os.environ.get('GOOGLE_CLIENT_ID')),
        'linkedin': bool(os.environ.get('LINKEDIN_CLIENT_ID')),
        'magic_link': True
    }
    
    # Get linked providers
    linked_providers = {
        provider.provider: provider 
        for provider in auth_providers
    }
    
    context = {
        'auth_providers': auth_providers,
        'available_providers': available_providers,
        'linked_providers': linked_providers,
    }
    
    return render(request, 'users/auth_settings.html', context)

@login_required
@require_http_methods(["POST"])
def link_auth_method(request):
    """Initiate linking of a new authentication method"""
    provider = request.POST.get('provider')
    
    if not provider:
        return JsonResponse({'error': 'Provider is required'}, status=400)
    
    # Check if already linked
    if AuthProvider.objects.filter(user=request.user, provider=provider, is_verified=True).exists():
        return JsonResponse({'error': 'This authentication method is already linked'}, status=400)
    
    # Create linking token
    token = MultiAuthHandler.create_linking_token(request.user, provider)
    
    # Generate appropriate linking URL based on provider
    if provider == 'google':
        # Redirect to Google OAuth with linking token in state
        google_oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'redirect_uri': f"{request.build_absolute_uri('/users/auth/callback/google/')}",
            'response_type': 'code',
            'scope': 'email profile',
            'state': json.dumps({'linking_token': token})
        }
        return JsonResponse({'redirect_url': f"{google_oauth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"})
    
    elif provider == 'linkedin':
        # Redirect to LinkedIn OAuth with linking token in state
        linkedin_oauth_url = f"https://www.linkedin.com/oauth/v2/authorization"
        params = {
            'client_id': os.environ.get('LINKEDIN_CLIENT_ID'),
            'redirect_uri': f"{request.build_absolute_uri('/users/auth/callback/linkedin/')}",
            'response_type': 'code',
            'scope': 'r_liteprofile r_emailaddress',
            'state': json.dumps({'linking_token': token})
        }
        return JsonResponse({'redirect_url': f"{linkedin_oauth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"})
    
    elif provider == 'email':
        # For email/password, show a form to set password
        return JsonResponse({'action': 'show_password_form', 'token': token})
    
    elif provider == 'magic_link':
        # Send magic link to user's email
        # This would integrate with Supertokens passwordless flow
        return JsonResponse({'action': 'magic_link_sent', 'email': request.user.email})
    
    return JsonResponse({'error': 'Unsupported provider'}, status=400)

@login_required
@require_http_methods(["POST"])
def unlink_auth_method(request):
    """Remove a linked authentication method"""
    provider = request.POST.get('provider')
    
    if not provider:
        return JsonResponse({'error': 'Provider is required'}, status=400)
    
    # Check that user has at least one other verified auth method
    verified_count = AuthProvider.objects.filter(
        user=request.user, 
        is_verified=True
    ).count()
    
    if verified_count <= 1:
        return JsonResponse({
            'error': 'You must have at least one authentication method linked to your account'
        }, status=400)
    
    # Unlink the provider
    AuthProvider.objects.filter(user=request.user, provider=provider).delete()
    
    messages.success(request, f'{provider.title()} authentication has been unlinked from your account')
    return JsonResponse({'success': True})

@csrf_exempt
def oauth_callback(request, provider):
    """Handle OAuth callbacks for linking accounts"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code or not state:
        messages.error(request, 'Invalid OAuth callback')
        return redirect('auth_settings')
    
    try:
        state_data = json.loads(state)
        token = state_data.get('linking_token')
        
        if not token:
            messages.error(request, 'Invalid linking token')
            return redirect('auth_settings')
        
        # Verify token
        try:
            link_token = AuthLinkingToken.objects.get(
                token=token,
                is_used=False
            )
            
            if link_token.is_expired():
                messages.error(request, 'Linking token has expired')
                return redirect('auth_settings')
            
            # Exchange code for user info
            if provider == 'google':
                user_info = exchange_google_code(code, request)
            elif provider == 'linkedin':
                user_info = exchange_linkedin_code(code, request)
            else:
                messages.error(request, 'Unsupported provider')
                return redirect('auth_settings')
            
            # Link the auth provider
            MultiAuthHandler.link_auth_provider(
                user=link_token.user,
                provider=provider,
                provider_email=user_info['email'],
                provider_user_id=user_info['id'],
                auto_verify=True
            )
            
            # Mark token as used
            link_token.is_used = True
            link_token.save()
            
            messages.success(request, f'{provider.title()} authentication has been successfully linked to your account')
            
        except AuthLinkingToken.DoesNotExist:
            messages.error(request, 'Invalid or expired linking token')
            
    except json.JSONDecodeError:
        messages.error(request, 'Invalid state parameter')
    
    return redirect('auth_settings')

def exchange_google_code(code, request):
    """Exchange Google OAuth code for user info"""
    # Exchange code for tokens
    token_response = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': request.build_absolute_uri('/users/auth/callback/google/'),
        'grant_type': 'authorization_code'
    })
    
    tokens = token_response.json()
    
    # Get user info
    user_response = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f"Bearer {tokens['access_token']}"}
    )
    
    user_data = user_response.json()
    return {
        'id': user_data['id'],
        'email': user_data['email'],
        'name': user_data.get('name', '')
    }

def exchange_linkedin_code(code, request):
    """Exchange LinkedIn OAuth code for user info"""
    # Exchange code for tokens
    token_response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data={
        'code': code,
        'client_id': os.environ.get('LINKEDIN_CLIENT_ID'),
        'client_secret': os.environ.get('LINKEDIN_CLIENT_SECRET'),
        'redirect_uri': request.build_absolute_uri('/users/auth/callback/linkedin/'),
        'grant_type': 'authorization_code'
    })
    
    tokens = token_response.json()
    
    # Get user info
    headers = {'Authorization': f"Bearer {tokens['access_token']}"}
    
    # Get profile
    profile_response = requests.get(
        'https://api.linkedin.com/v2/me',
        headers=headers
    )
    profile_data = profile_response.json()
    
    # Get email
    email_response = requests.get(
        'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
        headers=headers
    )
    email_data = email_response.json()
    
    return {
        'id': profile_data['id'],
        'email': email_data['elements'][0]['handle~']['emailAddress'],
        'name': f"{profile_data.get('localizedFirstName', '')} {profile_data.get('localizedLastName', '')}".strip()
    }

@login_required
@require_http_methods(["POST"])
def set_password_for_linking(request):
    """Set password for email/password authentication linking"""
    token = request.POST.get('token')
    password = request.POST.get('password')
    
    if not token or not password:
        return JsonResponse({'error': 'Token and password are required'}, status=400)
    
    try:
        link_token = AuthLinkingToken.objects.get(
            token=token,
            provider='email',
            is_used=False
        )
        
        if link_token.is_expired():
            return JsonResponse({'error': 'Token has expired'}, status=400)
        
        # Set password for user
        user = link_token.user
        user.set_password(password)
        user.save()
        
        # Link email/password auth
        MultiAuthHandler.link_auth_provider(
            user=user,
            provider='email',
            provider_email=user.email,
            auto_verify=True
        )
        
        # Mark token as used
        link_token.is_used = True
        link_token.save()
        
        return JsonResponse({'success': True, 'message': 'Email/password authentication has been enabled'})
        
    except AuthLinkingToken.DoesNotExist:
        return JsonResponse({'error': 'Invalid token'}, status=400)