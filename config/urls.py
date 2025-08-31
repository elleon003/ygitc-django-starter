from django.contrib import admin, include
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
]
