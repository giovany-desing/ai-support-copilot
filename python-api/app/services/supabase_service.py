"""
Servicio de Supabase
Maneja todas las operaciones con la base de datos
"""

from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from app.config import settings

# Configurar logger
logger = logging.getLogger(__name__)

# ============================================
# CLASE SUPABASE SERVICE
# ============================================

class SupabaseService:
    """
    Servicio para interactuar con Supabase
    Maneja operaciones CRUD sobre la tabla tickets
    """

    def __init__(self):
        """Inicializar cliente de Supabase"""
        try:
            self.client: Client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_key
            )
            logger.info("✅ Cliente Supabase inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando Supabase: {str(e)}")
            raise

    # ============================================
    # OPERACIONES DE LECTURA
    # ============================================

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener un ticket por su ID

        Args:
            ticket_id: UUID del ticket

        Returns:
            Dict con datos del ticket o None si no existe

        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            logger.info(f"📋 Obteniendo ticket: {ticket_id}")

            response = self.client.table("tickets").select("*").eq("id", ticket_id).execute()

            if response.data and len(response.data) > 0:
                logger.info(f"✅ Ticket {ticket_id} encontrado")
                return response.data[0]
            else:
                logger.warning(f"⚠️ Ticket {ticket_id} no encontrado")
                return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo ticket {ticket_id}: {str(e)}")
            raise

    def get_tickets(
        self,
        limit: int = 50,
        offset: int = 0,
        processed: Optional[bool] = None,
        category: Optional[str] = None,
        sentiment: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtener lista de tickets con filtros opcionales

        Args:
            limit: Cantidad máxima de tickets
            offset: Offset para paginación
            processed: Filtrar por estado procesado
            category: Filtrar por categoría
            sentiment: Filtrar por sentimiento

        Returns:
            Lista de tickets

        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            logger.info(f"📋 Obteniendo tickets (limit={limit}, offset={offset})")

            # Construir query base
            query = self.client.table("tickets").select("*")

            # Aplicar filtros opcionales
            if processed is not None:
                query = query.eq("processed", processed)

            if category:
                query = query.eq("category", category)

            if sentiment:
                query = query.eq("sentiment", sentiment)

            # Aplicar ordenamiento, limit y offset
            response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

            logger.info(f"✅ Obtenidos {len(response.data)} tickets")
            return response.data

        except Exception as e:
            logger.error(f"❌ Error obteniendo tickets: {str(e)}")
            raise

    # ============================================
    # OPERACIONES DE ESCRITURA
    # ============================================

    def create_ticket(self, description: str) -> Dict[str, Any]:
        """
        Crear un nuevo ticket

        Args:
            description: Descripción del ticket

        Returns:
            Dict con el ticket creado

        Raises:
            Exception: Si hay error al crear
        """
        try:
            logger.info(f"📝 Creando nuevo ticket")

            ticket_data = {
                "description": description,
                "processed": False
            }

            response = self.client.table("tickets").insert(ticket_data).execute()

            if response.data and len(response.data) > 0:
                created_ticket = response.data[0]
                logger.info(f"✅ Ticket creado: {created_ticket['id']}")
                return created_ticket
            else:
                raise Exception("No se pudo crear el ticket")

        except Exception as e:
            logger.error(f"❌ Error creando ticket: {str(e)}")
            raise

    def update_ticket(
        self,
        ticket_id: str,
        category: Optional[str] = None,
        sentiment: Optional[str] = None,
        confidence: Optional[float] = None,
        reasoning: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        processing_time_ms: Optional[int] = None,
        llm_model: Optional[str] = None,
        processed: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Actualizar un ticket con resultados del procesamiento

        Args:
            ticket_id: UUID del ticket
            category: Categoría clasificada
            sentiment: Sentimiento detectado
            confidence: Nivel de confianza
            reasoning: Explicación de la clasificación
            keywords: Lista de palabras clave
            processing_time_ms: Tiempo de procesamiento
            llm_model: Modelo utilizado
            processed: Marcar como procesado

        Returns:
            Dict con el ticket actualizado

        Raises:
            Exception: Si hay error al actualizar
        """
        try:
            logger.info(f"📝 Actualizando ticket: {ticket_id}")

            # Construir objeto de actualización solo con campos no-None
            update_data = {}

            if category is not None:
                update_data["category"] = category

            if sentiment is not None:
                update_data["sentiment"] = sentiment

            if confidence is not None:
                update_data["confidence"] = confidence

            if reasoning is not None:
                update_data["reasoning"] = reasoning

            if keywords is not None:
                update_data["keywords"] = keywords

            if processing_time_ms is not None:
                update_data["processing_time_ms"] = processing_time_ms

            if llm_model is not None:
                # Truncar a 200 caracteres (límite de VARCHAR(200) en BD)
                if len(llm_model) > 200:
                    logger.warning(f"⚠️ llm_model truncado de {len(llm_model)} a 200 caracteres")
                    update_data["llm_model"] = llm_model[:197] + "..."
                else:
                    update_data["llm_model"] = llm_model

            if processed is not None:
                update_data["processed"] = processed

            # Ejecutar actualización
            response = self.client.table("tickets").update(update_data).eq("id", ticket_id).execute()

            if response.data and len(response.data) > 0:
                logger.info(f"✅ Ticket {ticket_id} actualizado correctamente")
                return response.data[0]
            else:
                raise Exception(f"No se pudo actualizar el ticket {ticket_id}")

        except Exception as e:
            logger.error(f"❌ Error actualizando ticket {ticket_id}: {str(e)}")
            raise

    def mark_as_processed(
        self,
        ticket_id: str,
        category: str,
        sentiment: str,
        confidence: float,
        reasoning: str,
        keywords: List[str],
        processing_time_ms: int,
        llm_model: str
    ) -> Dict[str, Any]:
        """
        Marcar un ticket como procesado con todos los resultados

        Args:
            ticket_id: UUID del ticket
            category: Categoría clasificada
            sentiment: Sentimiento detectado
            confidence: Nivel de confianza
            reasoning: Explicación
            keywords: Palabras clave
            processing_time_ms: Tiempo de procesamiento
            llm_model: Modelo utilizado

        Returns:
            Dict con el ticket actualizado
        """
        return self.update_ticket(
            ticket_id=ticket_id,
            category=category,
            sentiment=sentiment,
            confidence=confidence,
            reasoning=reasoning,
            keywords=keywords,
            processing_time_ms=processing_time_ms,
            llm_model=llm_model,
            processed=True
        )

    # ============================================
    # OPERACIONES DE ELIMINACIÓN (Opcional)
    # ============================================

    def delete_ticket(self, ticket_id: str) -> bool:
        """
        Eliminar un ticket

        Args:
            ticket_id: UUID del ticket

        Returns:
            True si se eliminó correctamente

        Raises:
            Exception: Si hay error al eliminar
        """
        try:
            logger.info(f"🗑️ Eliminando ticket: {ticket_id}")

            response = self.client.table("tickets").delete().eq("id", ticket_id).execute()

            logger.info(f"✅ Ticket {ticket_id} eliminado")
            return True

        except Exception as e:
            logger.error(f"❌ Error eliminando ticket {ticket_id}: {str(e)}")
            raise

    # ============================================
    # UTILIDADES
    # ============================================

    def health_check(self) -> bool:
        """
        Verificar conectividad con Supabase

        Returns:
            True si la conexión está activa
        """
        try:
            # Intenta hacer una query simple para verificar conexión
            response = self.client.table("tickets").select("id").limit(1).execute()
            logger.info("✅ Conexión con Supabase: OK")
            return True
        except Exception as e:
            logger.error(f"❌ Error en conexión con Supabase: {str(e)}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de tickets

        Returns:
            Dict con estadísticas
        """
        try:
            logger.info("📊 Obteniendo estadísticas de tickets")

            # Total de tickets
            total_response = self.client.table("tickets").select("id", count="exact").execute()
            total = total_response.count if total_response.count else 0

            # Tickets procesados
            processed_response = self.client.table("tickets").select("id", count="exact").eq("processed", True).execute()
            processed = processed_response.count if processed_response.count else 0

            # Tickets pendientes
            pending = total - processed

            stats = {
                "total": total,
                "processed": processed,
                "pending": pending,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"✅ Estadísticas: {stats}")
            return stats

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
            raise


# ============================================
# INSTANCIA GLOBAL (Singleton pattern)
# ============================================

_supabase_service_instance: Optional[SupabaseService] = None

def get_supabase_service() -> SupabaseService:
    """
    Obtener instancia singleton del servicio de Supabase

    Returns:
        SupabaseService instance
    """
    global _supabase_service_instance

    if _supabase_service_instance is None:
        _supabase_service_instance = SupabaseService()

    return _supabase_service_instance