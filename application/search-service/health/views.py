from django.http import JsonResponse

def health_check(request):
    # search-service is stateless: no database to probe.
    return JsonResponse({
        "status": "healthy",
        "service": "search-service",
        "apps": ["search"]
    }, status=200)
