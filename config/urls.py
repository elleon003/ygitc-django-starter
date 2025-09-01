from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
