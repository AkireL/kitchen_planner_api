import os

FRONTEND_URL = os.getenv('FRONTEND_URL')

ORIGINS = [
    FRONTEND_URL,
]

SENTRY_DSN = os.getenv("SENTRY_DSN")