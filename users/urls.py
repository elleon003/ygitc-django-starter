from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.user_settings_view, name='user_settings'),
    
    # Authentication management
    path('auth/settings/', auth_views.auth_settings_view, name='auth_settings'),
    path('auth/link/', auth_views.link_auth_method, name='link_auth_method'),
    path('auth/unlink/', auth_views.unlink_auth_method, name='unlink_auth_method'),
    path('auth/callback/<str:provider>/', auth_views.oauth_callback, name='oauth_callback'),
    path('auth/set-password/', auth_views.set_password_for_linking, name='set_password_for_linking'),
]
