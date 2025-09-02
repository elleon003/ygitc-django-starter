import os
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, passwordless, thirdparty, session, dashboard, userroles, usermetadata
from supertokens_python.recipe.thirdparty.provider import ProviderInput, ProviderConfig, ProviderClientConfig
from supertokens_python.recipe.passwordless import ContactEmailOrPhoneConfig
from typing import Dict, Any

def get_api_domain():
    return os.environ.get('SUPERTOKENS_API_DOMAIN', 'http://localhost:8000')

def get_website_domain():
    return os.environ.get('SUPERTOKENS_WEBSITE_DOMAIN', 'http://localhost:8000')

def get_supertokens_config():
    return SupertokensConfig(
        connection_uri=os.environ.get('SUPERTOKENS_CONNECTION_URI', 'https://try.supertokens.com'),
        api_key=os.environ.get('SUPERTOKENS_API_KEY', ''),
    )

def get_app_info():
    return InputAppInfo(
        app_name=os.environ.get('SUPERTOKENS_APP_NAME', 'Django Starter'),
        api_domain=get_api_domain(),
        website_domain=get_website_domain(),
        api_base_path="/auth",
        website_base_path="/auth"
    )

def get_recipe_list():
    # Import overrides here to avoid circular import
    from users.supertokens_auth import override_email_password_apis, override_third_party_apis, override_passwordless_apis
    
    return [
        session.init(),
        thirdparty.init(
            sign_in_and_up_feature=thirdparty.SignInAndUpFeature([
                # Google Provider
                ProviderInput(
                    config=ProviderConfig(
                        third_party_id="google",
                        clients=[
                            ProviderClientConfig(
                                client_id=os.environ.get('GOOGLE_CLIENT_ID', ''),
                                client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', ''),
                            ),
                        ],
                    ),
                ),
                # LinkedIn Provider  
                ProviderInput(
                    config=ProviderConfig(
                        third_party_id="linkedin",
                        clients=[
                            ProviderClientConfig(
                                client_id=os.environ.get('LINKEDIN_CLIENT_ID', ''),
                                client_secret=os.environ.get('LINKEDIN_CLIENT_SECRET', ''),
                            ),
                        ],
                    ),
                ),
            ]),
            override=thirdparty.InputOverrideConfig(
                apis=override_third_party_apis
            )
        ),
        passwordless.init(
            contact_config=ContactEmailOrPhoneConfig(),
            flow_type="MAGIC_LINK",
            override=passwordless.InputOverrideConfig(
                apis=override_passwordless_apis
            )
        ),
        emailpassword.init(
            override=emailpassword.InputOverrideConfig(
                apis=override_email_password_apis
            )
        ),
        dashboard.init(),
        userroles.init(),
        usermetadata.init(),
    ]

def init_supertokens():
    init(
        app_info=get_app_info(),
        supertokens_config=get_supertokens_config(),
        framework='django',
        recipe_list=get_recipe_list(),
        mode='asgi',
    )