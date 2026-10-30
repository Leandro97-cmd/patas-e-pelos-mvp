"""Padrões de segurança. Segredos são fornecidos pelo ambiente na inicialização."""

from datetime import timedelta


class Config:
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Habilitar em HTTPS com PATAS_COOKIE_SECURE=1.
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_REFRESH_EACH_REQUEST = False
    MAX_CONTENT_LENGTH = 64 * 1024
