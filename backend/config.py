"""
DataFair Backend - Konfigurationsdatei
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Basis-Konfiguration"""
    # Sicherheit
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT Konfiguration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Datenbank
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'datafair.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS Einstellungen
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:5500', 'http://127.0.0.1:8080', 'http://localhost:8080'] # Frontend URLs
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = "redis://localhost:6379"  # Optional: Redis für Rate Limiting


class DevelopmentConfig(Config):
    """Entwicklungs-Konfiguration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Produktions-Konfiguration"""
    DEBUG = False
    TESTING = False
    # Weitere Produktions-spezifische Einstellungen


class TestingConfig(Config):
    """Test-Konfiguration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    

# Konfigurationen verfügbar machen
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
