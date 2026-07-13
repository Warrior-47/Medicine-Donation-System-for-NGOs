"""HTTP client for the internal APIs of the other services."""

import requests
from django.conf import settings


class ServiceUnavailable(Exception):
    """A dependent service could not be reached or returned an error."""


def internal_get(base_url, path, params=None, timeout=5):
    """GET an internal API endpoint.

    Returns the decoded JSON body, or None when the endpoint answers 404.
    Raises ServiceUnavailable on network errors and non-2xx responses.
    """
    url = base_url.rstrip('/') + path
    try:
        response = requests.get(
            url,
            params=params,
            headers={'X-Internal-Token': settings.INTERNAL_API_TOKEN},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise ServiceUnavailable(f'GET {url} failed: {exc}') from exc

    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        raise ServiceUnavailable(f'GET {url} returned {response.status_code}')
    return response.json()
