import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    # Secret Keys
    SECRET_KEY = os.getenv("SECRET_KEY", "Medchat-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "prasad-medchat-change-in-production")
    
    # Database
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/medical-chatbot")
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_HOURS", 24)))
    
    # Flask Configuration
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # ===== GEMINI API CONFIGURATION =====
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # Fast and capable
    
    # RAG Data Paths
    DATA_PATH = os.getenv("DATA_PATH", "./data/medical_final_dataset.json")
    INDEX_PATH = os.getenv("INDEX_PATH", "./ai/index.faiss")
    
    # RAG Configuration
    CONTEXT_RETRIEVAL_K = int(os.getenv("CONTEXT_RETRIEVAL_K", 3))  # Number of context chunks
    MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", 500))  # Gemini can handle more
    RESPONSE_TEMPERATURE = float(os.getenv("RESPONSE_TEMPERATURE", 0.4))  # Balanced for quality
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/medical-chatbot-test"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)


# Select config based on environment
config_name = os.getenv("FLASK_ENV", "development").lower()
if config_name == "production":
    # Validate production configuration
    if not os.getenv("SECRET_KEY") or not os.getenv("JWT_SECRET_KEY"):
        raise ValueError("SECRET_KEY and JWT_SECRET_KEY must be set in production environment")
    app_config = ProductionConfig
elif config_name == "testing":
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig

