import secrets
from datetime import timedelta
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.utils import timezone
from supertokens_python import init
from supertokens_python.recipe import emailpassword, thirdparty, passwordless
from supertokens_python.recipe.emailpassword.interfaces import APIInterface as EmailPasswordAPIInterface
from supertokens_python.recipe.thirdparty.interfaces import APIInterface as ThirdPartyAPIInterface
from supertokens_python.recipe.passwordless.interfaces import APIInterface as PasswordlessAPIInterface
from supertokens_python.recipe.emailpassword.interfaces import SignUpPostOkResult, SignInPostOkResult
from supertokens_python.recipe.thirdparty.interfaces import SignInUpPostOkResult
from supertokens_python.types import APIResponse, GeneralErrorResponse
from .auth_models import AuthProvider, AuthLinkingToken

User = get_user_model()

class AuthenticationError(Exception):
    pass

class MultiAuthHandler:
    @staticmethod
    def get_or_create_user(email: str, provider: str, provider_user_id: Optional[str] = None) -> User:
        """Get existing user or create new one"""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email=email)
        return user
    
    @staticmethod
    def check_auth_method_linked(user: User, provider: str, provider_user_id: Optional[str] = None) -> bool:
        """Check if a specific auth method is linked to user account"""
        return AuthProvider.objects.filter(
            user=user,
            provider=provider,
            is_verified=True
        ).exists()
    
    @staticmethod
    def link_auth_provider(user: User, provider: str, provider_email: str, 
                          provider_user_id: Optional[str] = None, auto_verify: bool = False):
        """Link an authentication provider to a user account"""
        auth_provider, created = AuthProvider.objects.get_or_create(
            user=user,
            provider=provider,
            defaults={
                'provider_email': provider_email,
                'provider_user_id': provider_user_id,
                'is_verified': auto_verify
            }
        )
        
        if not created and not auth_provider.is_verified and auto_verify:
            auth_provider.is_verified = True
            auth_provider.save()
        
        return auth_provider
    
    @staticmethod
    def create_linking_token(user: User, provider: str) -> str:
        """Create a token for linking new auth methods"""
        token = secrets.token_urlsafe(32)
        AuthLinkingToken.objects.create(
            user=user,
            provider=provider,
            token=token,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        return token

def override_email_password_apis(original_implementation: EmailPasswordAPIInterface):
    original_sign_up = original_implementation.sign_up_post
    original_sign_in = original_implementation.sign_in_post
    
    async def sign_up_post(
        form_fields: list,
        tenant_id: str,
        api_options: Dict[str, Any],
        user_context: Dict[str, Any]
    ):
        email = None
        for field in form_fields:
            if field.id == "email":
                email = field.value
                break
        
        # Call original sign up
        response = await original_sign_up(form_fields, tenant_id, api_options, user_context)
        
        if isinstance(response, SignUpPostOkResult):
            # Create user in Django and link auth provider
            user = MultiAuthHandler.get_or_create_user(email, 'email')
            MultiAuthHandler.link_auth_provider(
                user=user,
                provider='email',
                provider_email=email,
                provider_user_id=response.user.user_id,
                auto_verify=True
            )
        
        return response
    
    async def sign_in_post(
        form_fields: list,
        tenant_id: str,
        api_options: Dict[str, Any],
        user_context: Dict[str, Any]
    ):
        email = None
        for field in form_fields:
            if field.id == "email":
                email = field.value
                break
        
        # Check if user exists and has email auth linked
        try:
            user = User.objects.get(email=email)
            if not MultiAuthHandler.check_auth_method_linked(user, 'email'):
                return GeneralErrorResponse(
                    "Email/password authentication is not enabled for this account. "
                    "Please use your configured authentication method or enable email/password in your account settings."
                )
        except User.DoesNotExist:
            pass  # Let original implementation handle
        
        # Call original sign in
        response = await original_sign_in(form_fields, tenant_id, api_options, user_context)
        
        if isinstance(response, SignInPostOkResult):
            # Update last used timestamp
            AuthProvider.objects.filter(
                user__email=email,
                provider='email'
            ).first().mark_used()
        
        return response
    
    original_implementation.sign_up_post = sign_up_post
    original_implementation.sign_in_post = sign_in_post
    
    return original_implementation

def override_third_party_apis(original_implementation: ThirdPartyAPIInterface):
    original_sign_in_up = original_implementation.sign_in_up_post
    
    async def sign_in_up_post(
        provider: Dict[str, Any],
        redirect_uri_info: Optional[Dict[str, Any]],
        oauth_tokens: Optional[Dict[str, Any]],
        tenant_id: str,
        api_options: Dict[str, Any],
        user_context: Dict[str, Any]
    ):
        # Get provider info from the request
        third_party_id = provider.id
        third_party_user_info = provider.get_user_info(oauth_tokens)
        email = third_party_user_info.email
        third_party_user_id = third_party_user_info.third_party_user_id
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            
            # Check if this auth method is linked
            if not MultiAuthHandler.check_auth_method_linked(user, third_party_id, third_party_user_id):
                return GeneralErrorResponse(
                    f"{third_party_id.title()} authentication is not enabled for this account. "
                    f"Please sign in with your existing method and link {third_party_id.title()} in your account settings."
                )
        except User.DoesNotExist:
            # New user - create and auto-link
            user = MultiAuthHandler.get_or_create_user(email, third_party_id, third_party_user_id)
        
        # Call original implementation
        response = await original_sign_in_up(
            provider, redirect_uri_info, oauth_tokens, 
            tenant_id, api_options, user_context
        )
        
        if isinstance(response, SignInUpPostOkResult):
            # Link or update auth provider
            MultiAuthHandler.link_auth_provider(
                user=user,
                provider=third_party_id,
                provider_email=email,
                provider_user_id=third_party_user_id,
                auto_verify=True
            )
            
            # Mark as used
            AuthProvider.objects.filter(
                user=user,
                provider=third_party_id
            ).first().mark_used()
        
        return response
    
    original_implementation.sign_in_up_post = sign_in_up_post
    
    return original_implementation

def override_passwordless_apis(original_implementation: PasswordlessAPIInterface):
    original_consume_code = original_implementation.consume_code_post
    
    async def consume_code_post(
        pre_auth_session_id: str,
        user_input_code: Optional[str],
        device_id: Optional[str],
        link_code: Optional[str],
        tenant_id: str,
        api_options: Dict[str, Any],
        user_context: Dict[str, Any]
    ):
        # This is called when user clicks magic link or enters code
        response = await original_consume_code(
            pre_auth_session_id, user_input_code, device_id,
            link_code, tenant_id, api_options, user_context
        )
        
        if hasattr(response, 'user'):
            email = response.user.email
            
            try:
                user = User.objects.get(email=email)
                
                # Check if magic link auth is enabled
                if not MultiAuthHandler.check_auth_method_linked(user, 'magic_link'):
                    return GeneralErrorResponse(
                        "Magic link authentication is not enabled for this account. "
                        "Please use your configured authentication method or enable magic link in your account settings."
                    )
            except User.DoesNotExist:
                # New user
                user = MultiAuthHandler.get_or_create_user(email, 'magic_link')
            
            # Link auth provider
            MultiAuthHandler.link_auth_provider(
                user=user,
                provider='magic_link',
                provider_email=email,
                provider_user_id=response.user.user_id,
                auto_verify=True
            )
            
            # Mark as used
            AuthProvider.objects.filter(
                user=user,
                provider='magic_link'
            ).first().mark_used()
        
        return response
    
    original_implementation.consume_code_post = consume_code_post
    
    return original_implementation