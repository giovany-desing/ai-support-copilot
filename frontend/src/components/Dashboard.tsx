import { useTickets, useMetrics } from '../hooks'

export const Dashboard = () => {
  const { tickets, loading } = useTickets()
  const metrics = useMetrics(tickets)

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-gray-100 rounded-lg p-6 animate-pulse h-32"></div>
        ))}
      </div>
    )
  }

  return (
    <div>
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        {/* Total Tickets */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium opacity-90">Total Tickets</span>
            <span className="text-2xl">📊</span>
          </div>
          <p className="text-4xl font-bold">{metrics.total}</p>
        </div>

        {/* Procesados */}
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium opacity-90">Procesados</span>
            <span className="text-2xl">✅</span>
          </div>
          <p className="text-4xl font-bold">{metrics.processed}</p>
          <p className="text-xs opacity-75 mt-1">
            {metrics.total > 0 ? ((metrics.processed / metrics.total) * 100).toFixed(0) : 0}% del total
          </p>
        </div>

        {/* Pendientes */}
        <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium opacity-90">Pendientes</span>
            <span className="text-2xl">⏳</span>
          </div>
          <p className="text-4xl font-bold">{metrics.pending}</p>
          <p className="text-xs opacity-75 mt-1">
            {metrics.total > 0 ? ((metrics.pending / metrics.total) * 100).toFixed(0) : 0}% del total
          </p>
        </div>

        {/* Negativos */}
        <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium opacity-90">Negativos</span>
            <span className="text-2xl">😟</span>
          </div>
          <p className="text-4xl font-bold">{metrics.negative}</p>
          <p className="text-xs opacity-75 mt-1">
            {metrics.processed > 0 ? ((metrics.negative / metrics.processed) * 100).toFixed(0) : 0}% procesados
          </p>
        </div>

        {/* Hoy */}
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium opacity-90">Hoy</span>
            <span className="text-2xl">📅</span>
          </div>
          <p className="text-4xl font-bold">{metrics.today}</p>
          <p className="text-xs opacity-75 mt-1">Tickets de hoy</p>
        </div>
      </div>

      {/* Distribución por Categoría */}
      <div className="bg-white rounded-lg border-2 border-gray-200 p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <span>📂</span> Distribución por Categoría
        </h3>

        {metrics.categoryDistribution.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No hay tickets procesados aún
          </p>
        ) : (
          <div className="space-y-3">
            {metrics.categoryDistribution.map((cat) => {
              const categoryColors = {
                Técnico: 'bg-blue-500',
                Facturación: 'bg-green-500',
                Comercial: 'bg-purple-500',
              }

              return (
                <div key={cat.category}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {cat.category}
                    </span>
                    <span className="text-sm text-gray-600">
                      {cat.count} tickets ({cat.percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                      className={`${categoryColors[cat.category]} h-full rounded-full transition-all duration-500`}
                      style={{ width: `${cat.percentage}%` }}
                    ></div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
