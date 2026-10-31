"""
Production settings. DEBUG=False, HTTPS enforced, security headers enabled.
"""

from .base import *   # noqa: F401,F403

# ─── Debug ───────────────────────────────────
DEBUG = False

# ─── Hosts ───────────────────────────────────
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')   # ← no default. Must be set in prod.

# ─── Security: HTTPS ─────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ─── Security: HSTS ──────────────────────────
SECURE_HSTS_SECONDS = 31536000   # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ─── Security: headers ───────────────────────
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# ─── Static / media (served by reverse proxy in prod) ────
# Django doesn't serve these files; nginx/S3 does. STATIC_ROOT and MEDIA_ROOT are
# still configured in base for `collectstatic` to copy files to a location the
# reverse proxy can serve.