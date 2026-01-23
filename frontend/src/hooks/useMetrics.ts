/**
 * Custom Hook: useMetrics
 * Calcula métricas y estadísticas basadas en los tickets
 */

import { useMemo } from 'react'
import type { Ticket, TicketMetrics, CategoryDistribution } from '../types'

export const useMetrics = (tickets: Ticket[]): TicketMetrics & {
  categoryDistribution: CategoryDistribution[]
} => {
  return useMemo(() => {
    const total = tickets.length
    const processed = tickets.filter((t) => t.processed).length
    const pending = total - processed
    const negative = tickets.filter((t) => t.sentiment === 'Negativo').length

    // Tickets de hoy
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const todayCount = tickets.filter((t) => {
      const ticketDate = new Date(t.created_at)
      ticketDate.setHours(0, 0, 0, 0)
      return ticketDate.getTime() === today.getTime()
    }).length

    // Distribución por categoría
    const categoryCount: Record<string, number> = {}
    tickets.forEach((ticket) => {
      if (ticket.category) {
        categoryCount[ticket.category] = (categoryCount[ticket.category] || 0) + 1
      }
    })

    const categoryDistribution: CategoryDistribution[] = Object.entries(categoryCount).map(
      ([category, count]) => ({
        category: category as any,
        count,
        percentage: total > 0 ? Math.round((count / total) * 100) : 0,
      })
    )

    return {
      total,
      processed,
      pending,
      negative,
      today: todayCount,
      categoryDistribution,
    }
  }, [tickets])
}
