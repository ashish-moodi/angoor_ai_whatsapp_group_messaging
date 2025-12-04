"""
URL configuration for whatsapp_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('whatsapp_groups.urls')),
]

