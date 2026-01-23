import { Ticket } from '../types/ticket'

interface TicketCardProps {
  ticket: Ticket
}

export const TicketCard = ({ ticket }: TicketCardProps) => {
  // Formatear fecha
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('es-ES', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  // Estilos por categoría
  const categoryStyles = {
    Técnico: 'bg-blue-100 text-blue-800 border-blue-300',
    Facturación: 'bg-green-100 text-green-800 border-green-300',
    Comercial: 'bg-purple-100 text-purple-800 border-purple-300',
  }

  // Estilos por sentimiento
  const sentimentStyles = {
    Positivo: 'bg-green-50 border-green-200',
    Neutral: 'bg-gray-50 border-gray-200',
    Negativo: 'bg-red-50 border-red-200',
  }

  // Emojis por sentimiento
  const sentimentEmoji = {
    Positivo: '😊',
    Neutral: '😐',
    Negativo: '😟',
  }

  return (
    <div
      className={`rounded-lg border-2 p-4 transition-all hover:shadow-md ${
        ticket.sentiment ? sentimentStyles[ticket.sentiment] : 'bg-white border-gray-200'
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-500 font-mono">
              #{ticket.id.slice(0, 8)}
            </span>
            {ticket.processed && (
              <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">
                ✓ Procesado
              </span>
            )}
            {!ticket.processed && (
              <span className="text-xs bg-yellow-500 text-white px-2 py-0.5 rounded-full">
                ⏳ Pendiente
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500">{formatDate(ticket.created_at)}</p>
        </div>

        {/* Sentimiento */}
        {ticket.sentiment && (
          <div className="flex items-center gap-1 text-2xl">
            <span>{sentimentEmoji[ticket.sentiment]}</span>
          </div>
        )}
      </div>

      {/* Descripción */}
      <p className="text-sm text-gray-800 mb-3 line-clamp-3">{ticket.description}</p>

      {/* Categoría y Confianza */}
      <div className="flex items-center gap-2 mb-3">
        {ticket.category && (
          <span
            className={`text-xs font-semibold px-3 py-1 rounded-full border ${
              categoryStyles[ticket.category]
            }`}
          >
            {ticket.category}
          </span>
        )}
        {ticket.confidence !== null && (
          <span className="text-xs text-gray-600 font-mono">
            {(ticket.confidence * 100).toFixed(0)}% confianza
          </span>
        )}
      </div>

      {/* Keywords */}
      {ticket.keywords && ticket.keywords.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {ticket.keywords.slice(0, 5).map((keyword, idx) => (
            <span
              key={idx}
              className="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded"
            >
              {keyword}
            </span>
          ))}
        </div>
      )}

      {/* Metadata */}
      {ticket.processed && (
        <div className="pt-2 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
          <span>
            {ticket.llm_model && `${ticket.llm_model}`}
          </span>
          {ticket.processing_time_ms && (
            <span>{ticket.processing_time_ms}ms</span>
          )}
        </div>
      )}
    </div>
  )
}
