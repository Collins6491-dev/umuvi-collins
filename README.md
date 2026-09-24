# Portfolio CMS

A database-driven personal software-engineering portfolio built with Django templates, HTML, CSS, vanilla JavaScript, GSAP, and ScrollTrigger. It has a custom permission-aware CMS, secure media handling, and a deliberately separate public and dashboard experience.

## Stack

- Python 3.13+ and Django 6
- SQLite in development; PostgreSQL-ready production settings
- Django ORM and built-in authentication/password reset tokens
- HTML5, CSS3, vanilla JavaScript, locally served GSAP 3.15 and ScrollTrigger
- Pillow for verified image uploads and `python-dotenv` for local configuration

## Structure

```text
config/                  Django settings, URLs, ASGI/WSGI
apps/core/               site configuration, security headers, SEO, shared utilities
apps/accounts/           throttled authentication and password recovery
apps/portfolio/          public profile, projects, career, skills, resume
apps/dashboard/          custom CMS screens and authorization-aware CRUD
apps/contact/            CSRF-protected, rate-limited contact form
templates/               shared, public, dashboard, authentication, error templates
static/                  CSS, vanilla JS, local GSAP assets, favicon
requirements/            development and production dependency sets
```

## Local setup

1. Create and activate a virtual environment.

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies and copy the environment template.

   ```powershell
   python -m pip install -r requirements/development.txt
   Copy-Item .env.example .env
   ```

3. Set a unique `SECRET_KEY` in `.env`, then create the database, default role groups, and a site administrator.

   ```powershell
   python manage.py migrate
   python manage.py bootstrap_roles
   python manage.py createsuperuser
   ```

   A user must be both `is_staff=True` and assigned appropriate Django permissions/group membership to use `/dashboard/`. A superuser has full access.

4. Run the application.

   ```powershell
   python manage.py runserver
   ```

Open `/dashboard/` to create the profile, site configuration, technologies, and truthfully documented projects. Published projects become visible on the public site; drafts do not.

## Content roles

- **Super Admin:** Django `is_superuser`; unrestricted.
- **Content Manager:** all public-content, media, settings, and contact-message permissions.
- **Editor:** portfolio CRUD without project publishing, profile/settings control, or contact-message access.
- **Viewer:** read-only portfolio CMS access.

Run `python manage.py bootstrap_roles` after migrations to create/update the groups. Grant `is_staff` deliberately for every dashboard user; group membership alone does not unlock it.

## Testing

```powershell
python manage.py test
python manage.py check
python manage.py makemigrations --check
```

The included tests exercise public draft visibility, dashboard access permissions, direct edit prevention, CSRF, contact rate limiting, CSP, and crawler directives.

## Production deployment

Use a managed PostgreSQL database and a least-privileged database user. Set these environment variables in the deployment platform—never commit them:

- `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SITE_URL`
- `DB_ENGINE=django.db.backends.postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, and `DEFAULT_FROM_EMAIL`

Before releasing:

```powershell
$env:DJANGO_SETTINGS_MODULE='config.settings.production'
python manage.py check --deploy
python manage.py collectstatic --noinput
```

Set `SITE_URL` to the public HTTPS origin (for example, `https://portfolio.example`) so password-reset emails never contain localhost or a proxy host. Gmail users should set `EMAIL_HOST=smtp.gmail.com`, `EMAIL_PORT=587`, `EMAIL_USE_TLS=True`, and use a Google App Password for `EMAIL_HOST_PASSWORD`—never a normal Google account password. Keep `.env` private; it is ignored by Git.

Production static assets are served from `STATIC_ROOT` by WhiteNoise. Install the production requirements and run `collectstatic --noinput` as part of every deployment; the storage backend creates hashed, compressed assets with safe cache headers. User-uploaded media must still be served from non-executable storage or a separate media origin.

## Security and performance notes

- State-changing requests use Django CSRF protection; dashboard permissions are checked server-side.
- Password resets use Django’s signed, expiring tokens and deliberately do not disclose account existence.
- Login and contact endpoints are rate-limited using Django’s cache. Use a shared cache such as Redis in multi-process production.
- Image and resume uploads use extension, size, claimed MIME, decoded-content/signature, and integrity validation with generated storage names.
- CSP, clickjacking protection, secure production cookies, HSTS, referrer policy, and conservative permissions policy are configured in settings/middleware.
- GSAP assets are served locally, respect reduced motion, and limit animation to opacity/transforms. Images have explicit dimensions and below-fold images lazy-load.

Lighthouse/PageSpeed scores depend on the final host, production images, font choices, and real content; measure them against the deployed URL rather than treating local development as a score.
