# ============================================
# AI Support Co-Pilot - Dockerfile
# Multi-stage build para optimizar tamaño
# ============================================

# ============================================
# STAGE 1: Builder
# ============================================
FROM python:3.11-slim as builder

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python en un directorio virtual
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# ============================================
# STAGE 2: Runtime
# ============================================
FROM python:3.11-slim

# Metadata
LABEL maintainer="AI Support Co-Pilot"
LABEL description="FastAPI backend with multi-model AI processing"

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser

# Configurar directorio de trabajo
WORKDIR /app

# Copiar dependencias desde builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY ./app ./app

# Cambiar permisos
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando para ejecutar la aplicación
# Usa PORT de Render si está disponible, sino usa 8000
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"