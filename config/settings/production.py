from urllib.parse import urlparse

from .base import *  # noqa: F403

DEBUG = False

if SECRET_KEY.startswith("unsafe-"):  # noqa: F405
    raise RuntimeError("SECRET_KEY must be set to a secure value in production.")

if not ALLOWED_HOSTS:  # noqa: F405
    raise RuntimeError("ALLOWED_HOSTS must be configured in production.")

site_url = urlparse(SITE_URL)  # noqa: F405
if (
    site_url.scheme != "https"
    or not site_url.hostname
    or site_url.hostname in {"localhost", "127.0.0.1"}
    or site_url.path not in {"", "/"}
    or site_url.params
    or site_url.query
    or site_url.fragment
):
    raise RuntimeError("SITE_URL must be the public HTTPS origin in production.")

# Serve collectstatic output from the application in production. This must sit
# directly after SecurityMiddleware, before the remaining middleware.
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

if EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":  # noqa: F405
    raise RuntimeError("Production email must use Django's SMTP email backend.")

missing_smtp_settings = [
    name
    for name, value in {
        "EMAIL_HOST": EMAIL_HOST,  # noqa: F405
        "EMAIL_HOST_USER": EMAIL_HOST_USER,  # noqa: F405
        "EMAIL_HOST_PASSWORD": EMAIL_HOST_PASSWORD,  # noqa: F405
        "DEFAULT_FROM_EMAIL": DEFAULT_FROM_EMAIL,  # noqa: F405
    }.items()
    if not value
]
if missing_smtp_settings:
    raise RuntimeError(
        "Missing production SMTP settings: " + ", ".join(missing_smtp_settings)
    )
