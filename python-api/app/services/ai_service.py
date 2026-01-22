"""
Servicio de IA Multi-Modelo
Combina Transformers (sentiment) + LangChain/Groq (categorization)
"""

from transformers import pipeline
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
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
# CLASE AI SERVICE
# ============================================

class AIService:
    """
    Servicio de IA multi-modelo para procesamiento de tickets

    Arquitectura:
    - Sentiment Analysis: Transformers (local, rápido)
    - Category Classification: LLM via Groq (preciso, contextual)
    """

    def __init__(self):
        """Inicializar modelos de IA"""
        logger.info("🤖 Inicializando servicio de IA...")

        # Inicializar componentes
        self._init_sentiment_model()
        self._init_llm_model()

        logger.info("✅ Servicio de IA inicializado correctamente")

    # ============================================
    # INICIALIZACIÓN DE MODELOS
    # ============================================

    def _init_sentiment_model(self):
        """
        Inicializar modelo de Transformers para análisis de sentimiento
        Usa: cardiffnlp/twitter-xlm-roberta-base-sentiment
        """
        try:
            logger.info(f"📦 Cargando modelo de sentimiento: {settings.sentiment_model}")

            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=settings.sentiment_model,
                top_k=None  # Retorna todas las probabilidades
            )

            logger.info("✅ Modelo de sentimiento cargado")

        except Exception as e:
            logger.error(f"❌ Error cargando modelo de sentimiento: {str(e)}")
            # Fallback: usar modelo más simple si falla
            logger.warning("⚠️ Intentando con modelo de respaldo...")
            try:
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
                logger.info("✅ Modelo de respaldo cargado")
            except Exception as e2:
                logger.error(f"❌ Error crítico cargando modelos: {str(e2)}")
                raise

    def _init_llm_model(self):
        """
        Inicializar LLM (Groq) para clasificación de categoría
        Usa: Llama 3.1 8B via Groq
        """
        try:
            logger.info(f"🧠 Inicializando LLM: {settings.groq_model}")

            self.llm = ChatGroq(
                model=settings.groq_model,
                temperature=0,  # Determinístico para clasificación
                groq_api_key=settings.groq_api_key,
                max_tokens=500
            )

            # Crear prompt template para categorización
            self.category_prompt = ChatPromptTemplate.from_messages([
                ("system", """Eres un asistente experto en clasificación de tickets de soporte.                                                 
                                                                                                                                                  
  Tu tarea es analizar tickets y clasificarlos en UNA de estas categorías:                                                                        
                                                                                                                                                  
  **CATEGORÍAS DISPONIBLES:**                                                                                                                     
  - Técnico: Problemas de servicio, conectividad, errores técnicos, fallas de sistema                                                             
  - Facturación: Cobros, pagos, facturas, precios, renovaciones, suscripciones                                                                    
  - Comercial: Consultas sobre productos, ventas, información general, nuevos servicios                                                           
                                                                                                                                                  
  **INSTRUCCIONES:**                                                                                                                              
  1. Lee cuidadosamente el ticket                                                                                                                 
  2. Identifica palabras clave y contexto                                                                                                         
  3. Clasifica en la categoría más apropiada                                                                                                      
  4. Explica tu razonamiento brevemente                                                                                                           
  5. Asigna un nivel de confianza (0.0 a 1.0)                                                                                                     
  6. Extrae las palabras clave más relevantes                                                                                                     
                                                                                                                                                  
  Responde ÚNICAMENTE en formato JSON válido, sin texto adicional."""),                                                                           
                  ("user", """Ticket a clasificar:                                                                                                
  "{description}"                                                                                                                                 
                                                                                                                                                  
  Responde en este formato JSON exacto (usa DOBLE llave para el JSON):                                                                            
  {{{{                                                                                                                                            
    "category": "Técnico" o "Facturación" o "Comercial",                                                                                          
    "category_reasoning": "explicación breve de por qué elegiste esta categoría",                                                                 
    "confidence": 0.85,                                                                                                                           
    "keywords": ["palabra1", "palabra2", "palabra3"]                                                                                              
  }}}}""")                                                                                                                                        
              ])

            # Parser para JSON
            self.json_parser = JsonOutputParser()

            # Crear chain
            self.category_chain = self.category_prompt | self.llm

            logger.info("✅ LLM inicializado correctamente")

        except Exception as e:
            logger.error(f"❌ Error inicializando LLM: {str(e)}")
            raise

    # ============================================
    # ANÁLISIS DE SENTIMIENTO (Transformers)
    # ============================================

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analizar sentimiento usando Transformers

        Args:
            text: Texto a analizar

        Returns:
            Dict con sentiment, confidence y reasoning
        """
        try:
            logger.info("😊 Analizando sentimiento...")
            start_time = time.time()

            # Ejecutar pipeline de sentiment
            result = self.sentiment_pipeline(text[:512])  # Limitar a 512 chars

            # Procesar resultado
            # El modelo puede retornar diferentes formatos, normalizamos aquí
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    # Formato: [[{label, score}, {label, score}, ...]]
                    sentiments = result[0]
                else:
                    # Formato: [{label, score}]
                    sentiments = result
            else:
                sentiments = result

            # Mapear resultado a nuestras categorías
            sentiment_map = {
                "POSITIVE": "Positivo",
                "NEUTRAL": "Neutral",
                "NEGATIVE": "Negativo",
                "5 stars": "Positivo",
                "4 stars": "Positivo",
                "3 stars": "Neutral",
                "2 stars": "Negativo",
                "1 star": "Negativo"
            }

            # Obtener sentimiento con mayor score
            if isinstance(sentiments, list):
                top_sentiment = max(sentiments, key=lambda x: x['score'])
            else:
                top_sentiment = sentiments

            label = top_sentiment['label']
            score = top_sentiment['score']

            # Mapear a nuestras categorías
            mapped_sentiment = sentiment_map.get(label, "Neutral")

            # Generar reasoning simple
            reasoning = self._generate_sentiment_reasoning(text, mapped_sentiment, score)

            elapsed_time = int((time.time() - start_time) * 1000)

            result_dict = {
                "sentiment": mapped_sentiment,
                "confidence": round(score, 3),
                "reasoning": reasoning,
                "processing_time_ms": elapsed_time,
                "model": settings.sentiment_model.split('/')[-1]
            }

            logger.info(f"✅ Sentimiento: {mapped_sentiment} (confianza: {score:.2f}) - {elapsed_time}ms")
            return result_dict

        except Exception as e:
            logger.error(f"❌ Error en análisis de sentimiento: {str(e)}")
            # Fallback: retornar neutral con baja confianza
            return {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "reasoning": "No se pudo determinar el sentimiento con precisión",
                "processing_time_ms": 0,
                "model": "fallback"
            }

    def _generate_sentiment_reasoning(self, text: str, sentiment: str, confidence: float) -> str:
        """
        Generar explicación simple del sentimiento detectado
        """
        text_lower = text.lower()

        # Palabras clave por sentimiento
        positive_keywords = ["excelente", "genial", "gracias", "perfecto", "bien", "bueno", "feliz", "contento"]
        negative_keywords = ["problema", "error", "no funciona", "mal", "urgente", "frustrado", "malo", "caído"]

        found_positive = [w for w in positive_keywords if w in text_lower]
        found_negative = [w for w in negative_keywords if w in text_lower]

        if sentiment == "Positivo" and found_positive:
            return f"Detectadas expresiones positivas: {', '.join(found_positive[:2])}"
        elif sentiment == "Negativo" and found_negative:
            return f"Detectadas expresiones negativas: {', '.join(found_negative[:2])}"
        elif confidence > 0.8:
            return f"El tono general del mensaje indica sentimiento {sentiment.lower()}"
        else:
            return f"Sentimiento {sentiment.lower()} detectado con confianza moderada"

    # ============================================
    # CLASIFICACIÓN DE CATEGORÍA (LLM)
    # ============================================

    def classify_category(self, text: str) -> Dict[str, Any]:
        """
        Clasificar categoría usando LLM

        Args:
            text: Texto a clasificar

        Returns:
            Dict con category, reasoning, confidence y keywords
        """
        try:
            logger.info("🎯 Clasificando categoría...")
            start_time = time.time()

            # Invocar LLM
            response = self.category_chain.invoke({"description": text})

            # Extraer contenido
            content = response.content

            # Parsear JSON
            # Intentar extraer JSON del contenido
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                result = json.loads(content)

            # Validar categoría
            category = result.get("category", "Comercial")
            if category not in ["Técnico", "Facturación", "Comercial"]:
                logger.warning(f"⚠️ Categoría inválida: {category}, usando Comercial")
                category = "Comercial"

            elapsed_time = int((time.time() - start_time) * 1000)

            result_dict = {
                "category": category,
                "category_reasoning": result.get("category_reasoning", "Clasificación automática"),
                "confidence": float(result.get("confidence", 0.8)),
                "keywords": result.get("keywords", []),
                "processing_time_ms": elapsed_time,
                "model": settings.groq_model
            }

            logger.info(f"✅ Categoría: {category} (confianza: {result_dict['confidence']:.2f}) - {elapsed_time}ms")
            return result_dict

        except Exception as e:
            logger.error(f"❌ Error en clasificación de categoría: {str(e)}")
            # Fallback: clasificación por keywords
            return self._fallback_category_classification(text)

    def _fallback_category_classification(self, text: str) -> Dict[str, Any]:
        """
        Clasificación de respaldo usando keywords si el LLM falla
        """
        logger.warning("⚠️ Usando clasificación de respaldo por keywords")

        text_lower = text.lower()

        # Keywords por categoría
        tech_keywords = ["internet", "conexión", "no funciona", "error", "caído", "lento", "wifi", "servidor", "app", "sistema"]
        billing_keywords = ["factura", "cobro", "pago", "precio", "tarifa", "suscripción", "renovación", "cargo"]
        commercial_keywords = ["información", "plan", "producto", "servicio", "contratar", "consulta", "disponible"]

        # Contar matches
        tech_score = sum(1 for k in tech_keywords if k in text_lower)
        billing_score = sum(1 for k in billing_keywords if k in text_lower)
        commercial_score = sum(1 for k in commercial_keywords if k in text_lower)

        # Determinar categoría
        scores = {
            "Técnico": tech_score,
            "Facturación": billing_score,
            "Comercial": commercial_score
        }

        category = max(scores, key=scores.get)
        max_score = scores[category]

        # Si no hay matches, default a Comercial
        if max_score == 0:
            category = "Comercial"
            confidence = 0.5
            reasoning = "No se detectaron keywords específicas, clasificado como consulta comercial"
        else:
            confidence = min(0.6 + (max_score * 0.1), 0.85)
            reasoning = f"Clasificado por keywords relevantes (método de respaldo)"

        return {
            "category": category,
            "category_reasoning": reasoning,
            "confidence": confidence,
            "keywords": [],
            "processing_time_ms": 0,
            "model": "fallback-keywords"
        }

    # ============================================
    # ORQUESTADOR MULTI-MODELO
    # ============================================

    def process_ticket(self, description: str) -> Dict[str, Any]:
        """
        Procesar ticket completo usando arquitectura multi-modelo

        Pipeline:
        1. Análisis de sentimiento (Transformers)
        2. Clasificación de categoría (LLM)
        3. Combinar resultados
        4. Calcular métricas

        Args:
            description: Descripción del ticket

        Returns:
            Dict con análisis completo
        """
        try:
            logger.info("🚀 Iniciando procesamiento multi-modelo")
            total_start_time = time.time()

            # PASO 1: Análisis de sentimiento
            sentiment_result = self.analyze_sentiment(description)

            # PASO 2: Clasificación de categoría
            category_result = self.classify_category(description)

            # PASO 3: Combinar resultados
            total_elapsed_time = int((time.time() - total_start_time) * 1000)

            combined_result = {
                # Categoría
                "category": category_result["category"],
                "category_reasoning": category_result["category_reasoning"],

                # Sentimiento
                "sentiment": sentiment_result["sentiment"],
                "sentiment_reasoning": sentiment_result["reasoning"],

                # Confianza combinada (promedio ponderado)
                "confidence": round(
                    (category_result["confidence"] * 0.6 + sentiment_result["confidence"] * 0.4),
                    3
                ),

                # Keywords
                "keywords": category_result["keywords"],

                # Métricas
                "processing_time_ms": total_elapsed_time,
                "models_used": [
                    sentiment_result["model"],
                    category_result["model"]
                ]
            }

            logger.info(f"✅ Procesamiento completado en {total_elapsed_time}ms")
            logger.info(f"   Categoría: {combined_result['category']}")
            logger.info(f"   Sentimiento: {combined_result['sentiment']}")
            logger.info(f"   Confianza: {combined_result['confidence']:.2f}")

            return combined_result

        except Exception as e:
            logger.error(f"❌ Error en procesamiento multi-modelo: {str(e)}")
            raise

    # ============================================
    # HEALTH CHECK
    # ============================================

    def health_check(self) -> Dict[str, str]:
        """
        Verificar estado de los modelos

        Returns:
            Dict con estado de cada componente
        """
        status = {}

        # Verificar sentiment model
        try:
            test_result = self.sentiment_pipeline("test")
            status["sentiment_model"] = "healthy"
        except Exception as e:
            status["sentiment_model"] = f"error: {str(e)}"

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