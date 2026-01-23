/**
 * Custom Hook: useTickets
 * Maneja la obtención y actualización en tiempo real de tickets
 */

import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabaseClient'
import type { Ticket } from '../types'
import type { RealtimeChannel, RealtimePostgresChangesPayload } from '@supabase/supabase-js'

interface UseTicketsReturn {
  tickets: Ticket[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export const useTickets = (): UseTicketsReturn => {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Función para obtener tickets
  const fetchTickets = async () => {
    try {
      setLoading(true)
      setError(null)

      const { data, error: fetchError } = await supabase
        .from('tickets')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100)

      if (fetchError) {
        throw fetchError
      }

      setTickets(data || [])
    } catch (err) {
      console.error('Error fetching tickets:', err)
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Fetch inicial
    fetchTickets()

    // Configurar suscripción a Realtime
    const channel: RealtimeChannel = supabase
      .channel('tickets-changes')
      .on(
        'postgres_changes',
        {
          event: '*', // Escuchar INSERT, UPDATE, DELETE
          schema: 'public',
          table: 'tickets',
        },
        (payload: RealtimePostgresChangesPayload<Ticket>) => {
          console.log('📡 Realtime event:', payload.eventType, payload)

          switch (payload.eventType) {
            case 'INSERT':
              // Agregar nuevo ticket al inicio
              setTickets((prev) => [payload.new as Ticket, ...prev])
              break

            case 'UPDATE':
              // Actualizar ticket existente
              setTickets((prev) =>
                prev.map((ticket) =>
                  ticket.id === payload.new.id
                    ? (payload.new as Ticket)
                    : ticket
                )
              )
              break

            case 'DELETE':
              // Eliminar ticket
              setTickets((prev) =>
                prev.filter((ticket) => ticket.id !== (payload.old as Ticket).id)
              )
              break
          }
        }
      )
      .subscribe((status: string) => {
        console.log('📡 Realtime subscription status:', status)
      })

    // Cleanup: cancelar suscripción cuando el componente se desmonte
    return () => {
      console.log('🔌 Unsubscribing from Realtime')
      supabase.removeChannel(channel)
    }
  }, [])

  return {
    tickets,
    loading,
    error,
    refetch: fetchTickets,
  }
}
