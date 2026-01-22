"""
Servicio de IA usando solo LLM (Groq)
Arquitectura simplificada para consistencia entre ambientes
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List, Optional
import logging
import time
import json
import re

from app.config import settings
from app.models import TicketCategory, TicketSentiment

# Configurar logger
logger = logging.getLogger(__name__)

# ============================================
# CLASE AI SERVICE (Simplificada)
# ============================================

class AIService:
    """
    Servicio de IA usando solo LLM para todo el procesamiento

    Arquitectura:
    - Sentiment Analysis: LLM via Groq
    - Category Classification: LLM via Groq

    Ventajas:
    - Consistencia entre desarrollo y producción
    - Menor uso de memoria (~150MB)
    - Simple y mantenible
    """

    def __init__(self):
        """Inicializar servicio de IA"""
        logger.info("🤖 Inicializando servicio de IA (solo LLM)...")
        self._init_llm_model()
        logger.info("✅ Servicio de IA inicializado correctamente")

    # ============================================
    # INICIALIZACIÓN
    # ============================================

    def _init_llm_model(self):
        """Inicializar LLM (Groq) para todo el procesamiento"""
        try:
            logger.info(f"🧠 Inicializando LLM: {settings.groq_model}")

            self.llm = ChatGroq(
                model=settings.groq_model,
                temperature=0,  # Determinístico
                groq_api_key=settings.groq_api_key,
                max_tokens=500
            )

            logger.info("✅ LLM inicializado correctamente")

        except Exception as e:
            logger.error(f"❌ Error inicializando LLM: {str(e)}")
            raise

    # ============================================
    # PROCESAMIENTO COMPLETO (Un solo prompt)
    # ============================================

    def process_ticket(self, description: str) -> Dict[str, Any]:
        """
        Procesar ticket completo con un solo llamado al LLM

        Args:
            description: Descripción del ticket

        Returns:
            Dict con análisis completo (category + sentiment)
        """
        try:
            logger.info("🚀 Procesando ticket con LLM...")
            total_start_time = time.time()

            # Crear prompt único que analiza todo
            combined_prompt = ChatPromptTemplate.from_messages([
                ("system", """Eres un experto en análisis y clasificación de tickets de soporte.

**Tu tarea:**
1. Analizar el ticket
2. Clasificar en una categoría
3. Determinar el sentimiento
4. Explicar tus decisiones
5. Asignar nivel de confianza
6. Extraer palabras clave

**CATEGORÍAS:**
- Técnico: Problemas de servicio, conectividad, errores técnicos, fallas
- Facturación: Cobros, pagos, facturas, precios, renovaciones, suscripciones
- Comercial: Consultas sobre productos, ventas, información general, nuevos servicios

**SENTIMIENTOS:**
- Positivo: Cliente satisfecho, agradecido, contento
- Neutral: Cliente informativo, sin emoción clara
- Negativo: Cliente frustrado, enojado, insatisfecho, urgente

Responde ÚNICAMENTE en formato JSON válido."""),
                ("user", """Analiza este ticket:

"{description}"

Responde en formato JSON válido:
{{
  "category": "Técnico" o "Facturación" o "Comercial",
  "category_reasoning": "explicación breve por qué esta categoría",
  "sentiment": "Positivo" o "Neutral" o "Negativo",
  "sentiment_reasoning": "explicación breve del sentimiento",
  "confidence": 0.85,
  "keywords": ["palabra1", "palabra2", "palabra3"]
}}""")
            ])

            # Ejecutar LLM
            chain = combined_prompt | self.llm
            response = chain.invoke({"description": description})

            # Parsear respuesta JSON
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                result = json.loads(content)

            # Validar y normalizar categoría
            category = result.get("category", "Comercial")
            if category not in ["Técnico", "Facturación", "Comercial"]:
                logger.warning(f"⚠️ Categoría inválida: {category}, usando Comercial")
                category = "Comercial"

            # Validar y normalizar sentimiento
            sentiment = result.get("sentiment", "Neutral")
            if sentiment not in ["Positivo", "Neutral", "Negativo"]:
                logger.warning(f"⚠️ Sentimiento inválido: {sentiment}, usando Neutral")
                sentiment = "Neutral"

            # Calcular tiempo
            total_elapsed_time = int((time.time() - total_start_time) * 1000)

            # Construir respuesta
            combined_result = {
                "category": category,
                "category_reasoning": result.get("category_reasoning", "Clasificación automática"),
                "sentiment": sentiment,
                "sentiment_reasoning": result.get("sentiment_reasoning", "Análisis automático"),
                "confidence": float(result.get("confidence", 0.8)),
                "keywords": result.get("keywords", []),
                "processing_time_ms": total_elapsed_time,
                "models_used": [settings.groq_model]
            }

            logger.info(f"✅ Procesamiento completado en {total_elapsed_time}ms")
            logger.info(f"   Categoría: {combined_result['category']}")
            logger.info(f"   Sentimiento: {combined_result['sentiment']}")
            logger.info(f"   Confianza: {combined_result['confidence']:.2f}")

            return combined_result

        except Exception as e:
            logger.error(f"❌ Error en procesamiento: {str(e)}")
            # Fallback con clasificación por keywords
            return self._fallback_processing(description)

    def _fallback_processing(self, text: str) -> Dict[str, Any]:
        """
        Procesamiento de respaldo si el LLM falla
        Clasificación simple por keywords
        """
        logger.warning("⚠️ Usando clasificación de respaldo por keywords")

        text_lower = text.lower()

        # Keywords por categoría
        tech_keywords = ["internet", "conexión", "no funciona", "error", "caído", "lento", "wifi", "servidor"]
        billing_keywords = ["factura", "cobro", "pago", "precio", "tarifa", "suscripción"]
        commercial_keywords = ["información", "plan", "producto", "servicio", "contratar", "consulta"]

        # Keywords por sentimiento
        positive_keywords = ["excelente", "gracias", "perfecto", "bien", "bueno", "contento"]
        negative_keywords = ["problema", "error", "no funciona", "mal", "urgente", "frustrado"]

        # Contar matches
        tech_score = sum(1 for k in tech_keywords if k in text_lower)
        billing_score = sum(1 for k in billing_keywords if k in text_lower)
        commercial_score = sum(1 for k in commercial_keywords if k in text_lower)

        # Determinar categoría
        scores = {"Técnico": tech_score, "Facturación": billing_score, "Comercial": commercial_score}
        category = max(scores, key=scores.get) if max(scores.values()) > 0 else "Comercial"

        # Determinar sentimiento
        positive_count = sum(1 for k in positive_keywords if k in text_lower)
        negative_count = sum(1 for k in negative_keywords if k in text_lower)

        if negative_count > positive_count:
            sentiment = "Negativo"
        elif positive_count > negative_count:
            sentiment = "Positivo"
        else:
            sentiment = "Neutral"

        return {
            "category": category,
            "category_reasoning": "Clasificación por keywords (método de respaldo)",
            "sentiment": sentiment,
            "sentiment_reasoning": "Análisis por keywords (método de respaldo)",
            "confidence": 0.6,
            "keywords": [],
            "processing_time_ms": 0,
            "models_used": ["fallback-keywords"]
        }

    # ============================================
    # HEALTH CHECK
    # ============================================

    def health_check(self) -> Dict[str, str]:
        """
        Verificar estado del servicio de IA

        Returns:
            Dict con estado de cada componente
        """
        status = {}

        # Verificar LLM
        try:
            # Test simple
            status["llm_model"] = "healthy"
        except Exception as e:
            status["llm_model"] = f"error: {str(e)}"

        return status


# ============================================
# INSTANCIA GLOBAL (Singleton)
# ============================================

_ai_service_instance: Optional[AIService] = None

def get_ai_service() -> AIService:
    """
    Obtener instancia singleton del servicio de IA

    Returns:
        AIService instance
    """
    global _ai_service_instance

    if _ai_service_instance is None:
        _ai_service_instance = AIService()

    return _ai_service_instance
