"""donation-service URL configuration.

Public paths (routed here by the gateway/ingress):
    /donations/*   donation requests, notifications, accept/reject/complete
    /health/       liveness/readiness probe
"""
from django.urls import path, include

urlpatterns = [
    path('donations/', include('DonationRequestSystem.urls')),
    path('health/', include('health.urls')),
]
