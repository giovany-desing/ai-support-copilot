"""
Configuración centralizada de la aplicación
Maneja variables de entorno y settings globales
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator, computed_field
from functools import lru_cache
from typing import List, Any
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
    api_port: int = Field(default=8000, description="Puerto de la API. En Render, usar variable PORT")

    # CORS - Campo como str para evitar parsing automático de JSON por Pydantic
    # Se convierte a List[str] mediante la propiedad cors_origins
    cors_origins_raw: str = Field(
        default="*",
        description="Orígenes CORS (string). Se convierte automáticamente a lista."
    )

    # Logging
    log_level: str = "INFO"

    @model_validator(mode="before")
    @classmethod
    def map_env_vars(cls, data: Any) -> Any:
        """
        Mapea variables de entorno específicas antes del parsing
        """
        if isinstance(data, dict):
            # Mapear CORS_ORIGINS (mayúsculas) a cors_origins_raw
            if "CORS_ORIGINS" in data:
                data["cors_origins_raw"] = data.pop("CORS_ORIGINS")
            
            # También mapear cors_origins (minúsculas) si existe
            if "cors_origins" in data:
                data["cors_origins_raw"] = data.pop("cors_origins")
            
            # Mapear PORT (de Render) a api_port si no está definido
            if "PORT" in data and "api_port" not in data:
                try:
                    data["api_port"] = int(data["PORT"])
                except (ValueError, TypeError):
                    pass  # Si PORT no es un número válido, usar default
        
        return data

    @property
    def cors_origins(self) -> List[str]:
        """
        Propiedad que convierte cors_origins_raw (str) a List[str]
        Maneja diferentes formatos: JSON array, string separado por comas, o string simple
        """
        cors_value = getattr(self, "cors_origins_raw", "*")
        
        if cors_value is None or (isinstance(cors_value, str) and not cors_value.strip()):
            return ["*"]
        
        if isinstance(cors_value, list):
            return cors_value
        
        if isinstance(cors_value, str):
            # Intentar parsear como JSON
            try:
                parsed = json.loads(cors_value)
                if isinstance(parsed, list):
                    return parsed
                return [parsed] if isinstance(parsed, str) else [str(parsed)]
            except (json.JSONDecodeError, ValueError):
                # Si no es JSON válido, tratar como string simple o separado por comas
                if "," in cors_value:
                    origins = [origin.strip() for origin in cors_value.split(",") if origin.strip()]
                    return origins if origins else ["*"]
                else:
                    return [cors_value.strip()]
        
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar campos extra (como cors_origins que es solo una propiedad)
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cached de Settings
    Usar @lru_cache evita recrear el objeto en cada llamada
    """
    return Settings()


# Instancia global de settings
settings = get_settings()