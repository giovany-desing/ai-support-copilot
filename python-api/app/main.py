"""
AI-Powered Support Co-Pilot API
Entry point de la aplicación FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.config import settings
from app.models import HealthCheckResponse

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CREAR APLICACIÓN FASTAPI
# ============================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🤖 **AI-Powered Support Co-Pilot API**

    Sistema inteligente de clasificación y análisis de tickets de soporte usando IA.

    ## Características

    * 🎯 **Clasificación automática** de tickets en categorías (Técnico, Facturación, Comercial)
    * 😊 **Análisis de sentimiento** (Positivo, Neutral, Negativo)
    * 🧠 **Multi-modelo**: Combina Transformers + LLMs para optimizar velocidad y precisión
    * 📊 **Explicabilidad**: Confidence scores y reasoning para cada clasificación
    * ⚡ **Rápido**: ~850ms de latencia promedio

    ## Tecnologías

    * FastAPI + Python 3.11
    * LangChain + Groq (Llama 3.1)
    * Transformers (XLM-RoBERTa)
    * Supabase (PostgreSQL)

    ## Endpoints Principales

    * `POST /process-ticket` - Procesar y clasificar un ticket
    * `GET /health` - Health check de la API
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ============================================
# CONFIGURAR CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# EVENT HANDLERS
# ============================================

@app.on_event("startup")
async def startup_event():
    """
    Ejecutado al iniciar la aplicación
    """
    logger.info("=" * 50)
    logger.info(f"🚀 Iniciando {settings.app_name} v{settings.app_version}")
    logger.info(f"🌍 Ambiente: {settings.environment}")
    logger.info(f"🔧 Log Level: {settings.log_level}")
    logger.info("=" * 50)

    # TODO: Aquí se pueden inicializar conexiones, cargar modelos, etc.
    # Por ahora solo logueamos el inicio
    logger.info("✅ API lista para recibir requests")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Ejecutado al apagar la aplicación
    """
    logger.info("🛑 Cerrando API...")
    # TODO: Aquí se pueden cerrar conexiones, liberar recursos, etc.
    logger.info("✅ API cerrada correctamente")

# ============================================
# ROOT ENDPOINT
# ============================================

@app.get(
    "/",
    tags=["General"],
    summary="Root endpoint",
    description="Información básica de la API"
)
async def root():
    """
    Endpoint raíz que retorna información básica de la API
    """
    return {
        "message": "🤖 AI-Powered Support Co-Pilot API",
        "version": settings.app_version,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@app.get(
    "/health",
    tags=["Health"],
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Verifica el estado de la API y sus dependencias"
)
async def health_check():
    """
    Health check endpoint

    Retorna el estado de la API y verifica la conectividad
    con servicios dependientes (Supabase, Groq, Transformers)
    """
    try:
        from app.services.supabase_service import get_supabase_service
        from app.services.ai_service import get_ai_service

        services_status = {}
        overall_healthy = True

        # Verificar Supabase
        try:
            supabase_service = get_supabase_service()
            supabase_healthy = supabase_service.health_check()
            services_status["supabase"] = "connected" if supabase_healthy else "error"
            if not supabase_healthy:
                overall_healthy = False
        except Exception as e:
            services_status["supabase"] = f"error: {str(e)[:50]}"
            overall_healthy = False

        # Verificar AI Service
        try:
            ai_service = get_ai_service()
            ai_health = ai_service.health_check()
            services_status["sentiment_model"] = ai_health.get("sentiment_model", "unknown")
            services_status["llm_model"] = ai_health.get("llm_model", "unknown")

            if "error" in str(ai_health.get("sentiment_model", "")):
                overall_healthy = False
            if "error" in str(ai_health.get("llm_model", "")):
                overall_healthy = False
        except Exception as e:
            services_status["ai_service"] = f"error: {str(e)[:50]}"
            overall_healthy = False

        # Determinar status general
        status = "healthy" if overall_healthy else "degraded"

        return HealthCheckResponse(
            status=status,
            version=settings.app_version,
            timestamp=datetime.now(),
            services=services_status
        )

    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": settings.app_version,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

# ============================================
# INCLUIR ROUTERS (Se agregarán después)
# ============================================

# Incluir routers 
from app.routers import tickets   
app.include_router(tickets.router, prefix="/api")  

# ============================================
# MANEJO DE ERRORES GLOBAL
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Manejador global de excepciones no capturadas
    """
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "detail": str(exc) if settings.environment == "development" else None,
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )

# ============================================
# INFORMACIÓN DE DEBUG (solo en desarrollo)
# ============================================

if settings.environment == "development":
    @app.get("/debug/config", tags=["Debug"], include_in_schema=False)
    async def debug_config():
        """
        Endpoint de debug para ver la configuración
        Solo disponible en ambiente de desarrollo
        """
        return {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "groq_model": settings.groq_model,
            "sentiment_model": settings.sentiment_model,
            "log_level": settings.log_level,
            "supabase_url": settings.supabase_url,
            # NO exponer API keys
            "groq_api_key": "***" if settings.groq_api_key else "not_set",
            "supabase_key": "***" if settings.supabase_key else "not_set"
        }

# ============================================
# PUNTO DE ENTRADA (si se ejecuta directamente)
# ============================================

if __name__ == "__main__":
    import uvicorn

    logger.info("🔥 Ejecutando servidor en modo desarrollo")
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,  # Auto-reload en desarrollo
        log_level=settings.log_level.lower()
    )