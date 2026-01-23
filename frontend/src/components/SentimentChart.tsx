import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Ticket } from '../types/ticket'

interface SentimentChartProps {
  tickets: Ticket[]
}

export const SentimentChart = ({ tickets }: SentimentChartProps) => {
  // Calcular distribución de sentimientos
  const processedTickets = tickets.filter((t) => t.processed && t.sentiment)

  const sentimentCounts = {
    Positivo: processedTickets.filter((t) => t.sentiment === 'Positivo').length,
    Neutral: processedTickets.filter((t) => t.sentiment === 'Neutral').length,
    Negativo: processedTickets.filter((t) => t.sentiment === 'Negativo').length,
  }

  const chartData = [
    { name: 'Positivo', value: sentimentCounts.Positivo, emoji: '😊' },
    { name: 'Neutral', value: sentimentCounts.Neutral, emoji: '😐' },
    { name: 'Negativo', value: sentimentCounts.Negativo, emoji: '😟' },
  ].filter((item) => item.value > 0) // Solo mostrar sentimientos con datos

  // Colores
  const COLORS = {
    Positivo: '#10B981',
    Neutral: '#6B7280',
    Negativo: '#EF4444',
  }

  // Custom label
  const renderCustomLabel = (entry: any) => {
    const percent = ((entry.value / processedTickets.length) * 100).toFixed(0)
    return `${entry.name} ${percent}%`
  }

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span>🎭</span> Distribución de Sentimientos
      </h3>

      {processedTickets.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No hay tickets procesados</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomLabel}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              animationDuration={800}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
              formatter={(value: number) => [`${value} tickets`, 'Cantidad']}
            />
            <Legend
              formatter={(value, entry: any) => `${entry.payload.emoji} ${value}`}
            />
          </PieChart>
        </ResponsiveContainer>
      )}

      {/* Stats adicionales */}
      {processedTickets.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-3 gap-4 text-center">
          {Object.entries(sentimentCounts).map(([sentiment, count]) => (
            <div key={sentiment}>
              <p className="text-2xl font-bold" style={{ color: COLORS[sentiment as keyof typeof COLORS] }}>
                {count}
              </p>
              <p className="text-xs text-gray-600">{sentiment}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
