import { useTickets } from '../hooks'
import { TicketCard } from './TicketCard'

interface TicketListProps {
  filter?: 'all' | 'processed' | 'pending' | 'negative'
}

export const TicketList = ({ filter = 'all' }: TicketListProps) => {
  const { tickets, loading, error, refetch } = useTickets()

  // Filtrar tickets según el filtro
  const filteredTickets = tickets.filter((ticket) => {
    switch (filter) {
      case 'processed':
        return ticket.processed
      case 'pending':
        return !ticket.processed
      case 'negative':
        return ticket.sentiment === 'Negativo'
      default:
        return true
    }
  })

  // Estados de carga y error
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
          <p className="text-gray-600">Cargando tickets...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-800 font-semibold mb-2">Error al cargar tickets</p>
        <p className="text-red-600 text-sm mb-4">{error}</p>
        <button
          onClick={refetch}
          className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
        >
          Reintentar
        </button>
      </div>
    )
  }

  // Sin tickets
  if (filteredTickets.length === 0) {
    return (
      <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-12 text-center">
        <div className="text-6xl mb-4">📭</div>
        <p className="text-gray-600 font-semibold mb-1">
          {filter === 'all' ? 'No hay tickets' : `No hay tickets ${getFilterLabel(filter)}`}
        </p>
        <p className="text-gray-500 text-sm">
          {filter === 'all'
            ? 'Los tickets aparecerán aquí automáticamente'
            : 'Intenta con otro filtro'}
        </p>
      </div>
    )
  }

  return (
    <div>
      {/* Header con contador */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">
          {getFilterLabel(filter)}{' '}
          <span className="text-gray-500 font-normal">({filteredTickets.length})</span>
        </h3>
        <button
          onClick={refetch}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          ↻ Actualizar
        </button>
      </div>

      {/* Grid de tickets */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTickets.map((ticket) => (
          <TicketCard key={ticket.id} ticket={ticket} />
        ))}
      </div>
    </div>
  )
}

// Helper para labels de filtros
function getFilterLabel(filter: string): string {
  switch (filter) {
    case 'processed':
      return 'Tickets Procesados'
    case 'pending':
      return 'Tickets Pendientes'
    case 'negative':
      return 'Tickets Negativos'
    default:
      return 'Todos los Tickets'
  }
}
