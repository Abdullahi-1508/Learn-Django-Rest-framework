"""
Development settings. DEBUG=True, permissive, debug toolbar enabled.
"""

from .base import *   # noqa: F401,F403

# ─── Debug ───────────────────────────────────
DEBUG = env.bool('DEBUG', default=True)

# ─── Hosts ───────────────────────────────────
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '0.0.0.0', 'web'])

# ─── Debug toolbar (dev only) ────────────────
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# ─── Email (console backend in dev) ──────────
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}