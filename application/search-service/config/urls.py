"""search-service URL configuration.

Public paths (routed here by the gateway/ingress):
    /search/*    NGO search and priority search
    /health/     liveness/readiness probe
"""
from django.urls import path, include

urlpatterns = [
    path('search/', include('search.urls')),
    path('health/', include('health.urls')),
]
