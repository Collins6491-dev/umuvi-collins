from .base import *  # noqa: F403

DEBUG = True
SECRET_KEY = env("SECRET_KEY", "development-only-key-do-not-deploy")  # noqa: F405
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")  # noqa: F405
SITE_URL = env("SITE_URL", "http://localhost:8000").rstrip("/")  # noqa: F405
# Local development can print reset emails to the terminal. Set EMAIL_BACKEND to
# the SMTP backend in .env when testing an actual provider locally.
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")  # noqa: F405
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "portfolio@example.com")  # noqa: F405
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
