from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            "status": "healthy",
            "database": "connected",
            "service": "user-service",
            "apps": ["account"]
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "database": "disconnected",
            "service": "user-service"
        }, status=503)
