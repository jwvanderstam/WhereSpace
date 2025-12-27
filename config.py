# -*- coding: utf-8 -*-
"""
WhereSpace Configuration
Centralized configuration for the unified application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# ============================================================================
# Flask Configuration
# ============================================================================
class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wherespace-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server settings
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # ============================================================================
    # PostgreSQL / pgvector Configuration
    # ============================================================================
    PG_HOST = os.environ.get('PG_HOST', 'localhost')
    PG_PORT = int(os.environ.get('PG_PORT', 5432))
    PG_DATABASE = os.environ.get('PG_DATABASE', 'vectordb')
    PG_USER = os.environ.get('PG_USER', 'postgres')
    PG_PASSWORD = os.environ.get('PG_PASSWORD', 'Mutsmuts10')
    PG_TABLE = os.environ.get('PG_TABLE', 'documents')
    
    # Connection pool settings
    PG_MIN_CONNECTIONS = int(os.environ.get('PG_MIN_CONNECTIONS', 2))
    PG_MAX_CONNECTIONS = int(os.environ.get('PG_MAX_CONNECTIONS', 10))
    
    # ============================================================================
    # Ollama Configuration
    # ============================================================================
    OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'localhost')
    OLLAMA_PORT = int(os.environ.get('OLLAMA_PORT', 11434))
    OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
    OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"
    OLLAMA_EMBED_URL = f"{OLLAMA_BASE_URL}/api/embeddings"
    OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
    
    # Model settings
    OLLAMA_EMBED_MODEL = os.environ.get('OLLAMA_EMBED_MODEL', 'nomic-embed-text')
    OLLAMA_EMBED_DIMENSION = int(os.environ.get('OLLAMA_EMBED_DIMENSION', 768))
    DEFAULT_LLM_MODEL = os.environ.get('DEFAULT_LLM_MODEL', 'llama3.1')
    
    # Model persistence
    MODEL_CONFIG_DIR = BASE_DIR / 'config'
    MODEL_CONFIG_FILE = MODEL_CONFIG_DIR / '.model_config.json'
    
    # ============================================================================
    # Document Processing Configuration
    # ============================================================================
    # Supported file types
    SUPPORTED_DOCUMENT_TYPES = ['pdf', 'docx', 'txt', 'md']
    
    # Size limits
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_CHUNK_SIZE = 1000  # characters
    CHUNK_OVERLAP = 200  # characters
    
    # Processing limits
    MAX_DOCUMENTS_PER_BATCH = 50
    EMBEDDING_BATCH_SIZE = 10
    MAX_WORKERS = 4  # Parallel processing
    
    # ============================================================================
    # RAG Configuration
    # ============================================================================
    # Retrieval settings
    DEFAULT_TOP_K = 10  # Number of chunks to retrieve
    MIN_SIMILARITY = 0.3  # Minimum cosine similarity threshold
    
    # Query settings
    QUERY_CACHE_TTL = 300  # 5 minutes
    MAX_CONTEXT_LENGTH = 4096  # tokens
    
    # LLM generation settings
    DEFAULT_TEMPERATURE = 0.2
    DEFAULT_TOP_P = 0.9
    DEFAULT_TOP_K = 40
    
    # ============================================================================
    # Application Settings
    # ============================================================================
    # Session settings
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Static files
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    TEMPLATE_FOLDER = 'templates'
    
    # Upload settings (for future document upload feature)
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
    
    # ============================================================================
    # Feature Flags
    # ============================================================================
    ENABLE_CHAT = True
    ENABLE_DOCUMENT_UPLOAD = False  # Future feature
    ENABLE_USER_AUTH = False  # Future feature
    ENABLE_API = True
    ENABLE_WEBSOCKETS = False  # Future feature
    
    # ============================================================================
    # Cache Configuration
    # ============================================================================
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # ============================================================================
    # Security Settings
    # ============================================================================
    # CORS settings (for API)
    CORS_ENABLED = os.environ.get('CORS_ENABLED', 'False').lower() == 'true'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Rate limiting (for future)
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_DEFAULT = '100/hour'
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        cls.MODEL_CONFIG_DIR.mkdir(exist_ok=True)
        if cls.ENABLE_DOCUMENT_UPLOAD:
            cls.UPLOAD_FOLDER.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Tighter security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use separate test database
    PG_DATABASE = 'vectordb_test'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config.get(env, config['default'])
    config_class.ensure_directories()
    
    return config_class
