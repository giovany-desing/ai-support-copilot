-- ============================================
-- AI-Powered Support Co-Pilot - Database Setup
-- ============================================
-- Tabla de tickets con campos para clasificación por IA
-- Incluye: RLS policies, índices y triggers

-- ============================================
-- 1. CREAR TABLA TICKETS
-- ============================================

CREATE TABLE IF NOT EXISTS tickets (
    -- Identificador único
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Timestamp de creación
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Contenido del ticket (campo requerido)
    description TEXT NOT NULL CHECK (char_length(description) > 0),
    
    -- Clasificación por IA
    category TEXT CHECK (category IN ('Técnico', 'Facturación', 'Comercial')),
    sentiment TEXT CHECK (sentiment IN ('Positivo', 'Neutral', 'Negativo')),
    
    -- Estado de procesamiento
    processed BOOLEAN DEFAULT FALSE,
    
    -- Campos adicionales para explicabilidad de IA
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    reasoning TEXT,
    keywords TEXT[],
    
    -- Métricas de performance
    processing_time_ms INTEGER,
    llm_model VARCHAR(200),
    
    -- Timestamp de última actualización
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 2. CREAR ÍNDICES PARA OPTIMIZAR QUERIES
-- ============================================

-- Índice para ordenar por fecha (queries más comunes)
CREATE INDEX IF NOT EXISTS idx_tickets_created_at
ON tickets(created_at DESC);

-- Índice para filtrar por categoría
CREATE INDEX IF NOT EXISTS idx_tickets_category
ON tickets(category)
WHERE category IS NOT NULL;

-- Índice para filtrar por sentimiento
CREATE INDEX IF NOT EXISTS idx_tickets_sentiment
ON tickets(sentiment)
WHERE sentiment IS NOT NULL;

-- Índice para filtrar tickets no procesados
CREATE INDEX IF NOT EXISTS idx_tickets_processed
ON tickets(processed)
WHERE processed = FALSE;

-- Índice compuesto para queries de dashboard
CREATE INDEX IF NOT EXISTS idx_tickets_dashboard
ON tickets(created_at DESC, category, sentiment, processed);

-- ============================================
-- 3. FUNCIÓN PARA ACTUALIZAR updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4. TRIGGER PARA ACTUALIZAR updated_at AUTOMÁTICAMENTE
-- ============================================

DROP TRIGGER IF EXISTS update_tickets_updated_at ON tickets;

CREATE TRIGGER update_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Habilitar RLS en la tabla
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;

-- Policy 1: Permitir lectura pública (SELECT)
-- Cualquiera puede leer los tickets
CREATE POLICY "Allow public read access"
    ON tickets
    FOR SELECT
    TO public
    USING (true);

-- Policy 2: Permitir inserción pública (INSERT)
-- Cualquiera puede crear tickets (simula usuarios creando tickets)
CREATE POLICY "Allow public insert"
    ON tickets
    FOR INSERT
    TO public
    WITH CHECK (true);

-- Policy 3: Permitir actualización pública (UPDATE)
-- Necesario para que la API pueda actualizar con resultados de IA
CREATE POLICY "Allow public update"
    ON tickets
    FOR UPDATE
    TO public
    USING (true)
    WITH CHECK (true);

-- Policy 4: Permitir eliminación pública (DELETE)
-- Para poder limpiar datos de prueba
CREATE POLICY "Allow public delete"
    ON tickets
    FOR DELETE
    TO public
    USING (true);

-- ============================================
-- 6. HABILITAR REALTIME PARA LA TABLA
-- ============================================

-- Esto permite que el frontend reciba actualizaciones en tiempo real
ALTER PUBLICATION supabase_realtime ADD TABLE tickets;

-- ============================================
-- 7. INSERTAR DATOS DE PRUEBA (OPCIONAL)
-- ============================================

-- Descomentar para insertar tickets de prueba
/*
INSERT INTO tickets (description, processed) VALUES
    ('Mi internet no funciona desde ayer, necesito ayuda urgente', false),
    ('Quiero información sobre los nuevos planes disponibles', false),
    ('Me cobraron dos veces este mes en mi factura', false),
    ('Excelente servicio, muy contentos con el producto', false),
    ('El router se desconecta cada 5 minutos', false);
*/

-- ============================================
-- 8. QUERIES ÚTILES PARA VERIFICAR
-- ============================================

-- Ver todos los tickets
-- SELECT * FROM tickets ORDER BY created_at DESC;

-- Ver tickets no procesados
-- SELECT * FROM tickets WHERE processed = FALSE;

-- Ver distribución por categoría
-- SELECT category, COUNT(*) as total FROM tickets GROUP BY category;

-- Ver distribución por sentimiento
-- SELECT sentiment, COUNT(*) as total FROM tickets GROUP BY sentiment;

-- Ver tickets con baja confianza (requieren revisión)
-- SELECT * FROM tickets WHERE confidence < 0.7 AND processed = TRUE;

-- ============================================
-- FIN DEL SETUP
-- ============================================

-- Para verificar que todo se creó correctamente:
SELECT 'Setup completado exitosamente!' as status;