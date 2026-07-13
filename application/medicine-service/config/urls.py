"""medicine-service URL configuration.

Public paths (routed here by the gateway/ingress):
    /            dashboard
    /edit-list/, /add-medicine/, /update-medicine/<pk>/, /delete-medicine/<pk>/
    /health/     liveness/readiness probe

Internal (cluster-only, token-protected):
    /api/medicines/*   medicine list API for search- and donation-service
"""
from django.urls import path, include

urlpatterns = [
    path('', include('DonationSystem.urls')),
    path('health/', include('health.urls')),
    path('api/medicines/', include('DonationSystem.api_urls')),
]
