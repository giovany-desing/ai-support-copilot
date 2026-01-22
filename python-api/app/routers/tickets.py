"""
Router para endpoints de tickets
Maneja el procesamiento y gestión de tickets
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
import time

from app.models import (
    ProcessTicketRequest,
    ProcessTicketResponse,
    AIAnalysisResult,
    ErrorResponse,
    TicketCategory,
    TicketSentiment
)
from app.services.ai_service import get_ai_service
from app.services.supabase_service import get_supabase_service

# Configurar logger
logger = logging.getLogger(__name__)

# ============================================
# CREAR ROUTER
# ============================================

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
    responses={
        404: {"model": ErrorResponse, "description": "Ticket no encontrado"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)

# ============================================
# ENDPOINT: PROCESAR TICKET
# ============================================

@router.post(
    "/process",
    response_model=ProcessTicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Procesar ticket con IA",
    description="""
    Procesa un ticket usando modelos de IA para:
    - Clasificar en categoría (Técnico, Facturación, Comercial)
    - Analizar sentimiento (Positivo, Neutral, Negativo)
    - Generar confidence score y reasoning

    ## Flujo:
    1. Recibe ticket_id y description
    2. Verifica que el ticket existe en Supabase
    3. Aplica análisis de sentimiento (Transformers)
    4. Aplica clasificación de categoría (LLM)
    5. Actualiza Supabase con resultados
    6. Retorna análisis completo

    ## Performance:
    - Latencia típica: 800-1000ms
    - Precisión: ~87%
    """,
    responses={
        200: {
            "description": "Ticket procesado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "ticket_id": "123e4567-e89b-12d3-a456-426614174000",
                        "analysis": {
                            "category": "Técnico",
                            "category_reasoning": "El ticket menciona problemas de conectividad",
                            "sentiment": "Negativo",
                            "sentiment_reasoning": "El cliente expresa frustración y urgencia",
                            "confidence": 0.89,
                            "keywords": ["internet", "no funciona", "urgente"],
                            "processing_time_ms": 847,
                            "models_used": ["xlm-roberta-sentiment", "llama-3.1-8b"]
                        },
                        "message": "Ticket procesado exitosamente"
                    }
                }
            }
        }
    }
)
async def process_ticket(request: ProcessTicketRequest):
    """
    Procesar un ticket con IA multi-modelo

    Args:
        request: ProcessTicketRequest con ticket_id y description

    Returns:
        ProcessTicketResponse con resultado del análisis

    Raises:
        HTTPException: Si ocurre algún error en el procesamiento
    """
    try:
        logger.info("=" * 60)
        logger.info(f"🎯 Procesando ticket: {request.ticket_id}")
        logger.info(f"📝 Descripción: {request.description[:100]}...")

        # Obtener servicios
        ai_service = get_ai_service()
        supabase_service = get_supabase_service()

        # PASO 1: Verificar que el ticket existe
        logger.info("📋 Verificando ticket en Supabase...")
        ticket = supabase_service.get_ticket(request.ticket_id)

        if not ticket:
            logger.warning(f"⚠️ Ticket {request.ticket_id} no encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket con ID {request.ticket_id} no encontrado"
            )

        logger.info(f"✅ Ticket encontrado: {ticket['id']}")

        # PASO 2: Procesar con IA multi-modelo
        logger.info("🤖 Iniciando procesamiento con IA...")
        start_time = time.time()

        analysis = ai_service.process_ticket(request.description)

        total_time = int((time.time() - start_time) * 1000)
        logger.info(f"✅ IA completada en {total_time}ms")

        # PASO 3: Actualizar ticket en Supabase
        logger.info("💾 Actualizando ticket en Supabase...")

        # Formatear nombres de modelos de forma más compacta
        models_str = ", ".join(analysis["models_used"])
        # Truncar a 200 caracteres si es necesario (límite de la BD)
        if len(models_str) > 200:
            models_str = models_str[:197] + "..."

        updated_ticket = supabase_service.mark_as_processed(
            ticket_id=request.ticket_id,
            category=analysis["category"],
            sentiment=analysis["sentiment"],
            confidence=analysis["confidence"],
            reasoning=f"Cat: {analysis['category_reasoning']} | Sent: {analysis['sentiment_reasoning']}",
            keywords=analysis["keywords"],
            processing_time_ms=analysis["processing_time_ms"],
            llm_model=models_str
        )

        logger.info(f"✅ Ticket actualizado en Supabase")

        # PASO 4: Construir response
        ai_result = AIAnalysisResult(
            category=TicketCategory(analysis["category"]),
            category_reasoning=analysis["category_reasoning"],
            sentiment=TicketSentiment(analysis["sentiment"]),
            sentiment_reasoning=analysis["sentiment_reasoning"],
            confidence=analysis["confidence"],
            keywords=analysis["keywords"],
            processing_time_ms=analysis["processing_time_ms"],
            models_used=analysis["models_used"]
        )

        response = ProcessTicketResponse(
            success=True,
            ticket_id=request.ticket_id,
            analysis=ai_result,
            message="Ticket procesado exitosamente"
        )

        logger.info("=" * 60)
        logger.info(f"✅ ÉXITO - Ticket {request.ticket_id} procesado")
        logger.info(f"   └─ Categoría: {analysis['category']}")
        logger.info(f"   └─ Sentimiento: {analysis['sentiment']}")
        logger.info(f"   └─ Confianza: {analysis['confidence']:.2f}")
        logger.info(f"   └─ Tiempo total: {total_time}ms")
        logger.info("=" * 60)

        return response

    except HTTPException:
        # Re-lanzar HTTPExceptions tal cual
        raise

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ERROR procesando ticket {request.ticket_id}")
        logger.error(f"   └─ Error: {str(e)}")
        logger.error("=" * 60, exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar ticket: {str(e)}"
        )


# ============================================
# ENDPOINT: OBTENER TICKET (Opcional - Plus)
# ============================================

@router.get(
    "/{ticket_id}",
    summary="Obtener ticket por ID",
    description="Retorna la información completa de un ticket específico"
)
async def get_ticket(ticket_id: str):
    """
    Obtener un ticket específico por su ID

    Args:
        ticket_id: UUID del ticket

    Returns:
        Información completa del ticket
    """
    try:
        logger.info(f"📋 Obteniendo ticket: {ticket_id}")

        supabase_service = get_supabase_service()
        ticket = supabase_service.get_ticket(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} no encontrado"
            )

        return ticket

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"❌ Error obteniendo ticket {ticket_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================
# ENDPOINT: LISTAR TICKETS (Opcional - Plus)
# ============================================

@router.get(
    "/",
    summary="Listar tickets",
    description="Retorna lista de tickets con filtros opcionales"
)
async def list_tickets(
    limit: int = 50,
    offset: int = 0,
    processed: bool = None,
    category: str = None,
    sentiment: str = None
):
    """
    Listar tickets con paginación y filtros
    """
    try:
        logger.info(f"📋 Listando tickets (limit={limit}, offset={offset})")

        supabase_service = get_supabase_service()
        tickets = supabase_service.get_tickets(
            limit=limit,
            offset=offset,
            processed=processed,
            category=category,
            sentiment=sentiment
        )

        return {
            "success": True,
            "count": len(tickets),
            "tickets": tickets
        }

    except Exception as e:
        logger.error(f"❌ Error listando tickets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================
# ENDPOINT: ESTADÍSTICAS (Plus)
# ============================================

@router.get(
    "/stats/overview",
    summary="Estadísticas de tickets",
    description="Retorna estadísticas generales del sistema"
)
async def get_stats():
    """
    Obtener estadísticas generales de tickets
    """
    try:
        logger.info("📊 Obteniendo estadísticas...")

        supabase_service = get_supabase_service()
        stats = supabase_service.get_stats()

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )