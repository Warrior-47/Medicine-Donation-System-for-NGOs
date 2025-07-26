from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            "status": "healthy",
            "database": "connected",
            "service": "medicine-donation-system",
            "apps": ["account", "DonationSystem", "DonationRequestSystem", "search"]
        }, status=200)
    
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "database": "disconnected"
        }, status=503)