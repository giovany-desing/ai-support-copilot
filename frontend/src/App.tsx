import { useState } from 'react'
import { Dashboard, Charts, TicketList } from './components'

type FilterType = 'all' | 'processed' | 'pending' | 'negative'

function App() {
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')

  const filters: { value: FilterType; label: string; emoji: string }[] = [
    { value: 'all', label: 'Todos', emoji: '📋' },
    { value: 'processed', label: 'Procesados', emoji: '✅' },
    { value: 'pending', label: 'Pendientes', emoji: '⏳' },
    { value: 'negative', label: 'Negativos', emoji: '😟' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-1">🤖 AI Support Co-Pilot</h1>
              <p className="text-blue-100 text-sm">
                Clasificación inteligente de tickets con IA en tiempo real
              </p>
            </div>
            <div className="hidden md:flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Realtime Activo</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Dashboard con KPIs */}
        <section>
          <Dashboard />
        </section>

        {/* Gráficos */}
        <section>
          <Charts />
        </section>

        {/* Lista de Tickets */}
        <section>
          <div className="bg-white rounded-lg border-2 border-gray-200 p-6 shadow-sm">
            {/* Header con filtros */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                📝 Listado de Tickets
              </h2>

              {/* Tabs de filtros */}
              <div className="flex flex-wrap gap-2">
                {filters.map((filter) => (
                  <button
                    key={filter.value}
                    onClick={() => setActiveFilter(filter.value)}
                    className={`px-4 py-2 rounded-lg font-medium transition-all ${
                      activeFilter === filter.value
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <span className="mr-2">{filter.emoji}</span>
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Lista de tickets */}
            <TicketList filter={activeFilter} />
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-sm text-gray-600">
              <p>
                <strong>AI Support Co-Pilot</strong> - Prueba Técnica Full-Stack AI Engineer
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Stack: React + TypeScript + Tailwind + Supabase Realtime + FastAPI + LangChain + Groq
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 transition-colors"
              >
                📦 GitHub
              </a>
              <a
                href="https://ai-support-copilot-api.onrender.com/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 transition-colors"
              >
                🔗 API Docs
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
