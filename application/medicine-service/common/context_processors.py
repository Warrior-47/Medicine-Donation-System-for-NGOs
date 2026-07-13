def user(request):
    """Expose request.user as {{ user }} in templates.

    Replaces django.contrib.auth.context_processors.auth, which is
    unavailable without the contrib.auth app.
    """
    return {'user': getattr(request, 'user', None)}
