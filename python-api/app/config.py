"""
Configuración centralizada de la aplicación
Maneja variables de entorno y settings globales
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings
    Lee automáticamente desde variables de entorno o archivo .env
    """

    # Información de la aplicación
    app_name: str = "AI Support Co-Pilot API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Supabase
    supabase_url: str
    supabase_key: str

    # Groq (LLM)
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"

    # AI Models
    sentiment_model: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS
    cors_origins: list = ["*"]  # En producción, especificar dominios exactos

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cached de Settings
    Usar @lru_cache evita recrear el objeto en cada llamada
    """
    return Settings()


# Instancia global de settings
settings = get_settings()