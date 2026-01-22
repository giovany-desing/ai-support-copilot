# 🗄️ Database Setup - Supabase                                                                                                                  
                                                                                                                                                  
  ## Descripción                                                                                                                                  
                                                                                                                                                  
  Configuración de la base de datos PostgreSQL en Supabase para el sistema de tickets.                                                            
                                                                                                                                                  
  ## Tabla: tickets                                                                                                                               
                                                                                                                                                  
  ### Campos Principales                                                                                                                          
                                                                                                                                                  
  | Campo | Tipo | Descripción |                                                                                                                  
  |-------|------|-------------|                                                                                                                  
  | `id` | UUID | Identificador único (PK) |                                                                                                      
  | `created_at` | TIMESTAMP | Fecha de creación automática |                                                                                     
  | `description` | TEXT | Contenido del ticket (requerido) |                                                                                     
  | `category` | TEXT | Clasificación por IA: Técnico, Facturación, Comercial |                                                                   
  | `sentiment` | TEXT | Análisis de sentimiento: Positivo, Neutral, Negativo |                                                                   
  | `processed` | BOOLEAN | Estado de procesamiento (default: false) |                                                                            
                                                                                                                                                  
  ### Campos de Explicabilidad                                                                                                                    
                                                                                                                                                  
  | Campo | Tipo | Descripción |                                                                                                                  
  |-------|------|-------------|                                                                                                                  
  | `confidence` | FLOAT | Nivel de confianza del modelo (0.0-1.0) |                                                                              
  | `reasoning` | TEXT | Explicación de la clasificación |                                                                                        
  | `keywords` | TEXT[] | Palabras clave identificadas |                                                                                          
                                                                                                                                                  
  ### Campos de Métricas                                                                                                                          
                                                                                                                                                  
  | Campo | Tipo | Descripción |                                                                                                                  
  |-------|------|-------------|                                                                                                                  
  | `processing_time_ms` | INTEGER | Tiempo de procesamiento en milisegundos |                                                                    
  | `llm_model` | VARCHAR(200) | Modelo utilizado |                                                                                                
  | `updated_at` | TIMESTAMP | Última actualización |                                                                                             
                                                                                                                                                  
  ## Índices Creados                                                                                                                              
                                                                                                                                                  
  - `idx_tickets_created_at` - Ordenamiento por fecha                                                                                             
  - `idx_tickets_category` - Filtrado por categoría                                                                                               
  - `idx_tickets_sentiment` - Filtrado por sentimiento                                                                                            
  - `idx_tickets_processed` - Filtrado por estado                                                                                                 
  - `idx_tickets_dashboard` - Queries compuestas para dashboard                                                                                   
                                                                                                                                                  
  ## Row Level Security (RLS)                                                                                                                     
                                                                                                                                                  
  Políticas configuradas:                                                                                                                         
  - ✅ Lectura pública (SELECT)                                                                                                                   
  - ✅ Inserción pública (INSERT)                                                                                                                 
  - ✅ Actualización pública (UPDATE)                                                                                                             
  - ✅ Eliminación pública (DELETE)                                                                                                               
                                                                                                                                                  
  > **Nota de seguridad:** En producción real, estas políticas deberían ser más restrictivas con autenticación por roles.                         
                                                                                                                                                  
  ## Realtime                                                                                                                                     
                                                                                                                                                  
  La tabla está habilitada para Realtime, permitiendo:                                                                                            
  - Actualizaciones automáticas en el frontend                                                                                                    
  - Notificaciones de nuevos tickets                                                                                                              
  - Sincronización en tiempo real                                                                                                                 
                                                                                                                                                  
  ## Instalación                                                                                                                                  
                                                                                                                                                  
  1. Crear proyecto en [supabase.com](https://supabase.com)                                                                                       
  2. Ir a SQL Editor                                                                                                                              
  3. Ejecutar `setup.sql`                                                                                                                         
  4. Verificar en Table Editor                                                                                                                    
                                                                                                                                                  
  ## Queries Útiles                                                                                                                               
                                                                                                                                                  
  ```sql                                                                                                                                          
  -- Ver todos los tickets                                                                                                                        
  SELECT * FROM tickets ORDER BY created_at DESC;                                                                                                 
                                                                                                                                                  
  -- Ver tickets pendientes                                                                                                                       
  SELECT * FROM tickets WHERE processed = FALSE;                                                                                                  
                                                                                                                                                  
  -- Métricas por categoría                                                                                                                       
  SELECT category, COUNT(*) as total                                                                                                              
  FROM tickets                                                                                                                                    
  GROUP BY category;                                                                                                                              
                                                                                                                                                  
  -- Tickets con baja confianza                                                                                                                   
  SELECT * FROM tickets                                                                                                                           
  WHERE confidence < 0.7 AND processed = TRUE;                                                                                                    
                                                                                                                                                  
  Configuración de Variables                                                                                                                      
                                                                                                                                                  
  En tu aplicación, necesitarás:                                                                                                                  
                                                                                                                                                  
  SUPABASE_URL=https://xxxxx.supabase.co                                                                                                          
  SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...                                                                                       
                                                                                                                                                  
  Obtén estas credenciales en: Settings > API