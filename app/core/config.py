"""
Core Configuration
Loads environment variables and application settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application Settings"""
    
    # Application
    APP_NAME: str = "Multi-Agent Voice AI System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_TTL: int = 3600
    REDIS_CACHE_TTL: int = 300
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WEBHOOK_URL: str = ""
    TWILIO_STATUS_CALLBACK_URL: str = ""
    
    # Deepgram STT
    DEEPGRAM_API_KEY: str = ""
    DEEPGRAM_MODEL: str = "nova-2"
    DEEPGRAM_LANGUAGE: str = "en-US"
    DEEPGRAM_INTERIM_RESULTS: bool = True
    
    # ElevenLabs TTS
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    ELEVENLABS_MODEL: str = "eleven_turbo_v2"
    
    # Deepgram TTS (Fallback)
    DEEPGRAM_TTS_MODEL: str = "aura-asteria-en"
    
    # Anthropic Claude
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 4096
    ANTHROPIC_TEMPERATURE: float = 0.7
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Groq (FREE alternative)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    LLM_PROVIDER: str = "anthropic"  # anthropic, openai, or groq
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_MENU: str = "menu_items"
    QDRANT_COLLECTION_FAQ: str = "faq_items"
    
    # Payment - Stripe
    STRIPE_API_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Payment - Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    
    PAYMENT_PROVIDER: str = "stripe"
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: str = ""
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_QUEUE_ORDERS: str = "orders_queue"
    RABBITMQ_QUEUE_NOTIFICATIONS: str = "notifications_queue"
    
    # Sentry
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "dev-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENCRYPTION_KEY: str = ""
    
    # TRAI Compliance
    TRAI_DND_CHECK_ENABLED: bool = True
    TRAI_CALLING_START_HOUR: int = 9
    TRAI_CALLING_END_HOUR: int = 21
    TRAI_TIMEZONE: str = "Asia/Kolkata"
    
    # TCPA Compliance
    TCPA_CALLING_START_HOUR: int = 8
    TCPA_CALLING_END_HOUR: int = 21
    
    # Recording
    RECORDING_CONSENT_REQUIRED: bool = True
    
    # Business Configuration
    ORDER_TIMEOUT_MINUTES: int = 60
    ORDER_PREPARATION_BUFFER_MINUTES: int = 5
    DELIVERY_RADIUS_KM: int = 10
    DRIVER_SEARCH_RADIUS_KM: int = 5
    DRIVER_ASSIGNMENT_TIMEOUT_SECONDS: int = 30
    REFUND_AUTO_APPROVE_AMOUNT: float = 50.0
    SUPPORT_ESCALATION_THRESHOLD: int = 3
    
    # Feature Flags
    FEATURE_SENTIMENT_ANALYSIS: bool = True
    FEATURE_CALL_RECORDING: bool = True
    FEATURE_MULTILANGUAGE: bool = True
    FEATURE_COST_OPTIMIZATION: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Caching
    CACHE_CUSTOMER_PROFILE_TTL: int = 300
    CACHE_MENU_ITEMS_TTL: int = 600
    CACHE_RESTAURANT_INFO_TTL: int = 300
    
    # Audio Processing
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1
    AUDIO_FORMAT: str = "mulaw"
    VAD_SILENCE_DURATION_MS: int = 1500
    INTERRUPT_DETECTION_THRESHOLD: float = 0.5
    
    # Cost Optimization
    USE_CHEAPER_TTS_FOR_CONFIRMATIONS: bool = True
    USE_CACHE_FOR_COMMON_RESPONSES: bool = True
    LLM_FALLBACK_ENABLED: bool = True
    
    # Testing
    TEST_MODE: bool = False
    MOCK_EXTERNAL_APIS: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
