"""Guard for the internal service-to-service API endpoints."""

import functools

from django.conf import settings
from django.http import JsonResponse


def require_internal_token(view):
    """Reject requests that don't carry the shared internal API token.

    The /api/* paths are never routed by the public gateway; this header
    check is defence in depth for traffic inside the cluster.
    """

    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        token = request.headers.get('X-Internal-Token')
        if token != settings.INTERNAL_API_TOKEN:
            return JsonResponse({'detail': 'invalid internal token'}, status=403)
        return view(request, *args, **kwargs)

    return wrapper
