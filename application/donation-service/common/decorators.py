"""View decorators for services without a users table."""

import functools
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect


def login_required(view):
    """Redirect anonymous users to user-service's login page.

    django.contrib.auth.decorators.login_required can't be used here: its
    anonymous-redirect path imports contrib.auth models, and this service
    installs neither contrib.auth nor contrib.contenttypes.
    """

    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            return view(request, *args, **kwargs)
        query = urlencode({'next': request.get_full_path()})
        return redirect(f'{settings.LOGIN_URL}?{query}')

    return wrapper
