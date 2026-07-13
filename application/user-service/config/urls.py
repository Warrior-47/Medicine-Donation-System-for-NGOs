"""user-service URL configuration.

Public paths (routed here by the gateway/ingress):
    /accounts/*  authentication pages
    /admin/*     Django admin (user management)
    /health/     liveness/readiness probe

Internal (cluster-only, token-protected):
    /api/*       user lookup API for the other services
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('account.urls')),
    path('health/', include('health.urls')),
    path('api/', include('account.api_urls')),
]
