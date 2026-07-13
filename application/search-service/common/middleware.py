"""request.user support for services that have no users table.

user-service stores user claims in the signed-cookie session at login
(see the cross-service contract in application/README.md). Any service
sharing SECRET_KEY can rebuild the user from those claims without a
database or network call.
"""

USER_INFO_SESSION_KEY = 'user_info'


class SessionUser:
    """Authenticated user reconstructed from session claims."""

    is_authenticated = True
    is_anonymous = False

    def __init__(self, claims):
        self.id = claims.get('id')
        self.pk = self.id
        self.username = claims.get('username', '')
        self.fullname = claims.get('fullname', '')
        self.email = claims.get('email', '')
        self.phone = claims.get('phone', '')
        self.is_ngo = bool(claims.get('is_ngo'))

    def __str__(self):
        return self.username


class AnonymousSessionUser:
    is_authenticated = False
    is_anonymous = True
    id = None
    pk = None
    username = ''
    fullname = ''
    email = ''
    phone = ''
    is_ngo = False

    def __str__(self):
        return 'AnonymousUser'


class SessionUserMiddleware:
    """Populate request.user from the shared session.

    Stands in for django.contrib.auth.middleware.AuthenticationMiddleware,
    which would need a local users table.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        claims = request.session.get(USER_INFO_SESSION_KEY)
        request.user = SessionUser(claims) if claims else AnonymousSessionUser()
        return self.get_response(request)
