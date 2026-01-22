"""
Configuración centralizada de la aplicación
Maneja variables de entorno y settings globales
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache
from typing import List
import json


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
    cors_origins: List[str] = Field(
        default=["*"],
        description="Lista de orígenes permitidos para CORS. Puede ser JSON string o lista."
    )

    # Logging
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Validador para cors_origins que maneja:
        - Listas ya parseadas
        - Strings JSON
        - Strings vacíos o None (retorna ["*"])
        - Strings simples separados por comas
        """
        if v is None:
            return ["*"]
        
        # Si ya es una lista, retornarla
        if isinstance(v, list):
            return v
        
        # Si es string, intentar parsearlo
        if isinstance(v, str):
            # Si está vacío, retornar default
            if not v.strip():
                return ["*"]
            
            # Intentar parsear como JSON
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                # Si es un string simple, convertirlo a lista
                return [parsed] if isinstance(parsed, str) else [str(parsed)]
            except (json.JSONDecodeError, ValueError):
                # Si no es JSON válido, tratar como string simple o separado por comas
                if "," in v:
                    # Separar por comas y limpiar espacios
                    return [origin.strip() for origin in v.split(",") if origin.strip()]
                else:
                    # String simple
                    return [v.strip()]
        
        # Fallback
        return ["*"]

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