"""Session key under which user claims are stored for the other services.

The session uses the signed-cookie backend, so any service sharing
SECRET_KEY can read these claims without a database or network call.
The key name is part of the cross-service contract - do not change it
without changing every service.
"""

USER_INFO_SESSION_KEY = 'user_info'


def build_user_claims(user):
    return {
        'id': user.id,
        'username': user.username,
        'fullname': user.fullname,
        'email': user.email,
        'phone': user.phone,
        'is_ngo': user.is_ngo,
    }
