import secrets


class SecurityHeadersMiddleware:
    """Add a restrictive baseline CSP without relying on a third-party package."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(16)
        response = self.get_response(request)
        directives = [
            "default-src 'self'",
            "base-uri 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "img-src 'self' data:",
            "style-src 'self'",
            f"script-src 'self' 'nonce-{request.csp_nonce}'",
            "font-src 'self'",
            "connect-src 'self'",
            "media-src 'self'",
            "worker-src 'self'",
        ]
        if request.is_secure():
            directives.append("upgrade-insecure-requests")
        response.headers.setdefault(
            "Content-Security-Policy",
            "; ".join(directives),
        )
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        return response
