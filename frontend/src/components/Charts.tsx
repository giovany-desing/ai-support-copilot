import { useTickets, useMetrics } from '../hooks'
import { CategoryChart } from './CategoryChart'
import { SentimentChart } from './SentimentChart'

export const Charts = () => {
  const { tickets, loading } = useTickets()
  const metrics = useMetrics(tickets)

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-100 rounded-lg h-96 animate-pulse"></div>
        <div className="bg-gray-100 rounded-lg h-96 animate-pulse"></div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <CategoryChart data={metrics.categoryDistribution} />
      <SentimentChart tickets={tickets} />
    </div>
  )
}
