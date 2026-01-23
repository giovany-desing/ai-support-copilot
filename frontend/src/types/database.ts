/**
 * Tipos generados para Supabase
 * Representa el schema de la base de datos
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      tickets: {
        Row: {
          id: string
          created_at: string
          description: string
          category: string | null
          sentiment: string | null
          processed: boolean
          confidence: number | null
          reasoning: string | null
          keywords: string[] | null
          processing_time_ms: number | null
          llm_model: string | null
          updated_at: string | null
        }
        Insert: {
          id?: string
          created_at?: string
          description: string
          category?: string | null
          sentiment?: string | null
          processed?: boolean
          confidence?: number | null
          reasoning?: string | null
          keywords?: string[] | null
          processing_time_ms?: number | null
          llm_model?: string | null
          updated_at?: string | null
        }
        Update: {
          id?: string
          created_at?: string
          description?: string
          category?: string | null
          sentiment?: string | null
          processed?: boolean
          confidence?: number | null
          reasoning?: string | null
          keywords?: string[] | null
          processing_time_ms?: number | null
          llm_model?: string | null
          updated_at?: string | null
        }
      }
    }
  }
}
