from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from common.session_claims import USER_INFO_SESSION_KEY, build_user_claims


@receiver(user_logged_in)
def store_user_claims_in_session(sender, request, user, **kwargs):
    """Copy user claims into the signed-cookie session at login.

    The other services have no users table; they authenticate requests
    purely from these claims.
    """
    request.session[USER_INFO_SESSION_KEY] = build_user_claims(user)
