import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { CategoryDistribution } from '../types/ticket'

interface CategoryChartProps {
  data: CategoryDistribution[]
}

export const CategoryChart = ({ data }: CategoryChartProps) => {
  // Mapear datos para Recharts
  const chartData = data.map((item) => ({
    name: item.category,
    Cantidad: item.count,
    Porcentaje: item.percentage,
  }))

  // Colores por categoría
  const categoryColor = {
    Técnico: '#3B82F6',
    Facturación: '#10B981',
    Comercial: '#8B5CF6',
  }

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span>📊</span> Tickets por Categoría
      </h3>

      {data.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No hay datos para mostrar</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" tick={{ fill: '#6b7280' }} />
            <YAxis tick={{ fill: '#6b7280' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
              formatter={(value: number, name: string) => {
                if (name === 'Cantidad') return [value, 'Tickets']
                if (name === 'Porcentaje') return [`${value.toFixed(1)}%`, 'Porcentaje']
                return [value, name]
              }}
            />
            <Legend />
            <Bar
              dataKey="Cantidad"
              fill="#3B82F6"
              radius={[8, 8, 0, 0]}
              animationDuration={800}
            />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
