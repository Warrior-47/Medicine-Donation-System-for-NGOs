#!/usr/bin/env python3
"""Local development gateway for the Medicine Donation System.

Simulates the Kubernetes ingress: serves the whole app on one host and
routes path prefixes to the four services, so cross-service links,
cookies and redirects behave exactly as they will in the cluster.

Pure standard library - no packages to install. Usage:

    python3 application/dev-gateway.py          # listens on :8080

with the services running on 127.0.0.1:8001-8004 (see README.md).
Override with env vars: GATEWAY_PORT, GATEWAY_BIND, USER_BACKEND,
MEDICINE_BACKEND, SEARCH_BACKEND, DONATION_BACKEND.
"""

import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

USER_BACKEND = os.environ.get('USER_BACKEND', 'http://127.0.0.1:8001')
MEDICINE_BACKEND = os.environ.get('MEDICINE_BACKEND', 'http://127.0.0.1:8002')
SEARCH_BACKEND = os.environ.get('SEARCH_BACKEND', 'http://127.0.0.1:8003')
DONATION_BACKEND = os.environ.get('DONATION_BACKEND', 'http://127.0.0.1:8004')

# First match wins. Mirrors the ingress path contract in README.md.
ROUTES = [
    ('/accounts/', USER_BACKEND),
    ('/admin/', USER_BACKEND),
    ('/static/account/', USER_BACKEND),   # login/register page assets
    ('/search/', SEARCH_BACKEND),
    ('/donations/', DONATION_BACKEND),
    ('/', MEDICINE_BACKEND),              # dashboard, medicine pages, shared /static/*
]

# Hop-by-hop headers must not be forwarded in either direction.
HOP_BY_HOP = {
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade', 'accept-encoding',
    'content-length',
}


class PassThroughRedirects(urllib.request.HTTPRedirectHandler):
    """Hand 3xx responses back to the browser instead of following them."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(PassThroughRedirects)


class GatewayHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _backend_for(self, path):
        for prefix, backend in ROUTES:
            if path.startswith(prefix):
                return backend
        return None

    def _proxy(self):
        # The internal service API is never exposed publicly.
        if self.path.startswith('/api/'):
            return self._simple_response(404, b'not routed\n')

        backend = self._backend_for(self.path)
        if backend is None:
            return self._simple_response(404, b'no route\n')

        length = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(length) if length else None

        headers = {
            k: v for k, v in self.headers.items()
            if k.lower() not in HOP_BY_HOP
        }
        if body is not None:
            headers['Content-Length'] = str(length)

        request = urllib.request.Request(
            backend + self.path, data=body, headers=headers,
            method=self.command,
        )
        try:
            response = OPENER.open(request, timeout=60)
        except urllib.error.HTTPError as exc:
            response = exc  # non-2xx responses (incl. 3xx) land here
        except urllib.error.URLError as exc:
            return self._simple_response(
                502, f'backend {backend} unreachable: {exc.reason}\n'.encode())

        payload = response.read()
        self.send_response(response.status)
        for key, value in response.headers.items():
            if key.lower() not in HOP_BY_HOP:
                self.send_header(key, value)
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(payload)

    def _simple_response(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = do_HEAD = _proxy

    def log_message(self, format, *args):  # quieter access log
        print(f'{self.address_string()} {self.command} {self.path} {args[-2] if len(args) > 1 else ""}')


def main():
    port = int(os.environ.get('GATEWAY_PORT', '8080'))
    bind = os.environ.get('GATEWAY_BIND', '0.0.0.0')
    server = ThreadingHTTPServer((bind, port), GatewayHandler)
    print(f'dev gateway listening on http://{bind}:{port}')
    for prefix, backend in ROUTES:
        print(f'  {prefix:<18} -> {backend}')
    server.serve_forever()


if __name__ == '__main__':
    main()
