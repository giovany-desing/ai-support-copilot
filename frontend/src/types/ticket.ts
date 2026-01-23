/**
 * Tipos de la aplicación
 * Modelos de negocio para tickets
 */

export type TicketCategory = 'Técnico' | 'Facturación' | 'Comercial'
export type TicketSentiment = 'Positivo' | 'Neutral' | 'Negativo'

export interface Ticket {
  id: string
  created_at: string
  description: string
  category: TicketCategory | null
  sentiment: TicketSentiment | null
  processed: boolean
  confidence: number | null
  reasoning: string | null
  keywords: string[] | null
  processing_time_ms: number | null
  llm_model: string | null
  updated_at: string | null
}

export interface TicketMetrics {
  total: number
  processed: number
  pending: number
  negative: number
  today: number
}

export interface CategoryDistribution {
  category: TicketCategory
  count: number
  percentage: number
}

export interface SentimentTrend {
  date: string
  Positivo: number
  Neutral: number
  Negativo: number
}
