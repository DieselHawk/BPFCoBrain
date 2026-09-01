"""Deployment configuration for Manus integration.

This module provides production-ready configuration for deploying BOB
to a server accessible from the Manus platform.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    
    # Flask
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # BOB
    BRAIN_VAULT = os.getenv("BRAIN_VAULT", str(Path.cwd() / "Brain"))
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", "credentials.json")
    GOOGLE_TOKEN = os.getenv("GOOGLE_TOKEN", "token.json")
    ONEDRIVE_TOKEN = os.getenv("ONEDRIVE_TOKEN", "onedrive_token.json")
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Manus Integration
    MANUS_API_URL = os.getenv("MANUS_API_URL", "https://evidportal-fvptvdpk.manus.space")
    MANUS_API_KEY = os.getenv("MANUS_API_KEY", "")
    
    # Security
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request
    PROPAGATE_EXCEPTIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Production security
    PREFERRED_URL_SCHEME = "https"


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


def get_config():
    """Get appropriate config based on environment."""
    env = os.getenv("FLASK_ENV", "production").lower()
    
    if env == "development":
        return DevelopmentConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return ProductionConfig()


__all__ = ["Config", "DevelopmentConfig", "ProductionConfig", "TestingConfig", "get_config"]
