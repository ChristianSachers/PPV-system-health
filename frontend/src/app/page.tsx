import Dashboard from '@/components/Dashboard'

export default function HomePage() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Campaign Fulfillment Dashboard
            </h2>
            <p className="mt-1 text-sm text-gray-600">
              Monitor impression delivery fulfillment across campaigns and deals.
              Identify system health patterns and investigate underperformance.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center text-sm">
              <div className="w-3 h-3 bg-fulfillment-excellent rounded-full mr-2"></div>
              <span className="text-gray-600">System Health: Optimal</span>
            </div>
          </div>
        </div>
      </div>

      <Dashboard />
    </div>
  )
}