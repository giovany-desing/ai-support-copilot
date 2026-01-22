"""
Modelos Pydantic para validación de datos
Define la estructura de requests y responses de la API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS - Valores permitidos
# ============================================

class TicketCategory(str, Enum):
    """Categorías posibles para tickets"""
    TECNICO = "Técnico"
    FACTURACION = "Facturación"
    COMERCIAL = "Comercial"


class TicketSentiment(str, Enum):
    """Sentimientos posibles detectados"""
    POSITIVO = "Positivo"
    NEUTRAL = "Neutral"
    NEGATIVO = "Negativo"


# ============================================
# REQUEST MODELS - Entrada de datos
# ============================================

class ProcessTicketRequest(BaseModel):
    """
    Request para procesar un ticket
    """
    ticket_id: str = Field(
        ...,
        description="UUID del ticket a procesar",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Descripción del ticket",
        example="Mi internet no funciona desde ayer, necesito ayuda urgente"
    )

    @validator('description')
    def description_must_not_be_empty(cls, v):
        """Validar que la descripción no esté vacía o solo espacios"""
        if not v or not v.strip():
            raise ValueError('La descripción no puede estar vacía')
        return v.strip()


class CreateTicketRequest(BaseModel):
    """
    Request para crear un nuevo ticket
    """
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Descripción del problema o consulta",
        example="Quiero información sobre los planes comerciales disponibles"
    )


# ============================================
# RESPONSE MODELS - Salida de datos
# ============================================

class AIAnalysisResult(BaseModel):
    """
    Resultado del análisis de IA
    """
    category: TicketCategory = Field(
        ...,
        description="Categoría identificada por IA"
    )
    category_reasoning: str = Field(
        ...,
        description="Explicación de por qué se eligió esta categoría",
        example="El ticket menciona problemas de conectividad y servicio técnico"
    )
    sentiment: TicketSentiment = Field(
        ...,
        description="Sentimiento detectado"
    )
    sentiment_reasoning: str = Field(
        ...,
        description="Explicación del sentimiento detectado",
        example="El cliente usa palabras como 'urgente' y 'no funciona', indicando frustración"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza del modelo (0.0 - 1.0)",
        example=0.87
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Palabras clave identificadas",
        example=["internet", "no funciona", "urgente"]
    )
    processing_time_ms: int = Field(
        ...,
        description="Tiempo de procesamiento en milisegundos",
        example=847
    )
    models_used: List[str] = Field(
        default_factory=list,
        description="Modelos de IA utilizados",
        example=["xlm-roberta-sentiment", "llama-3.1-8b"]
    )


class ProcessTicketResponse(BaseModel):
    """
    Response después de procesar un ticket
    """
    success: bool = Field(
        ...,
        description="Indica si el procesamiento fue exitoso"
    )
    ticket_id: str = Field(
        ...,
        description="UUID del ticket procesado"
    )
    analysis: AIAnalysisResult = Field(
        ...,
        description="Resultado del análisis de IA"
    )
    message: str = Field(
        default="Ticket procesado exitosamente",
        description="Mensaje descriptivo"
    )


class TicketResponse(BaseModel):
    """
    Representación completa de un ticket
    """
    id: str
    created_at: datetime
    description: str
    category: Optional[TicketCategory] = None
    sentiment: Optional[TicketSentiment] = None
    processed: bool = False
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    keywords: Optional[List[str]] = None
    processing_time_ms: Optional[int] = None
    llm_model: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Configuración del modelo"""
        from_attributes = True  # Permite crear desde ORM objects
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2026-01-21T10:30:00Z",
                "description": "Mi internet no funciona",
                "category": "Técnico",
                "sentiment": "Negativo",
                "processed": True,
                "confidence": 0.89,
                "reasoning": "El cliente reporta problema técnico con urgencia",
                "keywords": ["internet", "no funciona"],
                "processing_time_ms": 850,
                "llm_model": "llama-3.1-8b-instant",
                "updated_at": "2026-01-21T10:30:01Z"
            }
        }


# ============================================
# ERROR MODELS - Manejo de errores
# ============================================

class ErrorResponse(BaseModel):
    """
    Response estándar para errores
    """
    success: bool = False
    error: str = Field(
        ...,
        description="Mensaje de error",
        example="Ticket no encontrado"
    )
    detail: Optional[str] = Field(
        None,
        description="Detalles adicionales del error",
        example="No existe un ticket con el ID proporcionado"
    )
    error_code: Optional[str] = Field(
        None,
        description="Código de error para debugging",
        example="TICKET_NOT_FOUND"
    )


# ============================================
# HEALTH CHECK MODEL
# ============================================

class HealthCheckResponse(BaseModel):
    """
    Response del health check endpoint
    """
    status: str = Field(
        default="healthy",
        description="Estado de la API",
        example="healthy"
    )
    version: str = Field(
        ...,
        description="Versión de la API",
        example="1.0.0"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp del health check"
    )
    services: dict = Field(
        default_factory=dict,
        description="Estado de servicios dependientes",
        example={
            "supabase": "connected",
            "groq_llm": "available",
            "transformers": "loaded"
        }
    )