'use client'

/**
 * Dashboard Component - Campaign Fulfillment Analysis Interface
 *
 * Primary UI for system health monitoring and PM investigation workflows.
 * Implements TDD specifications from Dashboard.test.tsx with focus on:
 * - Fulfillment analysis and pattern recognition
 * - Campaign vs Deal distribution visualization
 * - Filtering and search capabilities for root cause investigation
 * - Drill-down navigation for detailed analysis
 */

import React, { useState, useEffect, useCallback } from 'react'
import {
  Search,
  Filter,
  Upload,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  ChevronDown
} from 'lucide-react'

import {
  Campaign,
  AnalyticsSummary,
  CampaignFilters,
  FulfillmentStatus,
  BaseComponentProps
} from '@/types'

import { campaignApi, analyticsApi, apiUtils } from '@/lib/api'
import {
  calculateSystemHealthMetrics,
  getCampaignsRequiringAttention,
  getFulfillmentStatus,
  getFulfillmentStatusClasses
} from '@/lib/fulfillment'

// Component imports
import SummaryCards from './dashboard/SummaryCards'
import CampaignTable from './dashboard/CampaignTable'
import ChartsSection from './dashboard/ChartsSection'
import SearchAndFilters from './dashboard/SearchAndFilters'
import CampaignDetailModal from './CampaignDetailModal'
import LoadingSpinner from './ui/LoadingSpinner'
import ErrorMessage from './ui/ErrorMessage'

interface DashboardProps extends BaseComponentProps {
  initialFilters?: CampaignFilters
}

const Dashboard: React.FC<DashboardProps> = ({
  className = '',
  'data-testid': testId = 'dashboard-main',
  initialFilters = {}
}) => {
  // State Management for Dashboard Data
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [analyticsSummary, setAnalyticsSummary] = useState<AnalyticsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<CampaignFilters>({
    type: 'all',
    status: 'all',
    fulfillment_status: 'all',
    search: '',
    ...initialFilters
  })

  // UI State
  const [selectedCampaigns, setSelectedCampaigns] = useState<string[]>([])
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [selectedCampaignId, setSelectedCampaignId] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  /**
   * Fetch dashboard data - campaigns and analytics summary
   * Implements API integration pattern from TDD specifications
   */
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Parallel API calls for optimal performance
      const [campaignsResponse, summaryResponse] = await Promise.all([
        campaignApi.getCampaigns(filters),
        analyticsApi.getSummary()
      ])

      setCampaigns(campaignsResponse.data)
      setAnalyticsSummary(summaryResponse)
      setLastUpdated(new Date())

    } catch (err) {
      const errorMessage = apiUtils.parseApiError(err)
      setError(errorMessage)
      console.error('Dashboard data fetch error:', err)
    } finally {
      setLoading(false)
    }
  }, [filters])

  /**
   * Handle filter changes with debounced API calls
   */
  const handleFiltersChange = useCallback((newFilters: CampaignFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
    setSelectedCampaigns([]) // Clear selections when filters change
  }, [])

  /**
   * Handle campaign selection for bulk operations
   */
  const handleCampaignSelection = useCallback((campaignIds: string[]) => {
    setSelectedCampaigns(campaignIds)
  }, [])

  /**
   * Handle drill-down navigation to campaign detail
   */
  const handleCampaignDrillDown = useCallback((campaign: Campaign) => {
    setSelectedCampaignId(campaign.id)
    setIsModalOpen(true)
  }, [])

  /**
   * Handle modal close
   */
  const handleModalClose = useCallback(() => {
    setIsModalOpen(false)
    setSelectedCampaignId(null)
  }, [])

  /**
   * Refresh dashboard data
   */
  const handleRefresh = useCallback(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  // Initial data load
  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  // Calculate derived metrics for system health analysis
  const systemHealthMetrics = React.useMemo(() => {
    return calculateSystemHealthMetrics(campaigns)
  }, [campaigns])

  const campaignsRequiringAttention = React.useMemo(() => {
    return getCampaignsRequiringAttention(campaigns)
  }, [campaigns])

  // Loading State
  if (loading && !campaigns.length) {
    return (
      <div
        className="flex items-center justify-center min-h-96"
        data-testid="loading-spinner"
      >
        <LoadingSpinner />
        <span className="ml-3 text-gray-600">Loading campaigns...</span>
      </div>
    )
  }

  // Error State
  if (error && !campaigns.length) {
    return (
      <ErrorMessage
        error={error}
        onRetry={handleRefresh}
        data-testid="error-message"
      />
    )
  }

  return (
    <main
      className={`space-y-6 ${className}`}
      data-testid={testId}
      role="main"
    >
      {/* Dashboard Header with Navigation and Actions */}
      <header
        className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4"
        data-testid="dashboard-header"
      >
        <div className="flex-1">
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-gray-900">
              Campaign Fulfillment Dashboard
            </h1>
            {campaignsRequiringAttention.length > 0 && (
              <div className="flex items-center text-sm text-fulfillment-warning">
                <AlertTriangle className="w-4 h-4 mr-1" />
                <span>{campaignsRequiringAttention.length} need attention</span>
              </div>
            )}
          </div>

          <div className="flex items-center mt-2 text-sm text-gray-600">
            <span>System Health: </span>
            <span
              className={`ml-1 font-medium ${
                systemHealthMetrics.overall_system_health === 'healthy'
                  ? 'text-fulfillment-excellent'
                  : systemHealthMetrics.overall_system_health === 'degraded'
                  ? 'text-fulfillment-warning'
                  : 'text-fulfillment-critical'
              }`}
            >
              {systemHealthMetrics.overall_system_health === 'healthy' && 'Optimal'}
              {systemHealthMetrics.overall_system_health === 'degraded' && 'Degraded'}
              {systemHealthMetrics.overall_system_health === 'critical' && 'Critical'}
            </span>
            {lastUpdated && (
              <span className="ml-4">
                Updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="btn btn-secondary text-sm"
            aria-label="Refresh dashboard data"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>

          <button
            className="btn btn-primary text-sm"
            aria-label="Upload campaigns"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload Campaigns
          </button>
        </div>
      </header>

      {/* Search and Filter Controls */}
      <SearchAndFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        campaignCount={campaigns.length}
        data-testid="search-and-filters"
      />

      {/* Summary Cards Section - KPI Overview */}
      <section data-testid="campaign-summary-cards">
        <SummaryCards
          analyticsSummary={analyticsSummary}
          systemHealthMetrics={systemHealthMetrics}
          campaignsRequiringAttention={campaignsRequiringAttention.length}
        />
      </section>

      {/* Main Dashboard Grid Layout */}
      <div
        className="dashboard-grid"
        data-testid="dashboard-grid"
      >
        {/* Analytics Charts Section */}
        <section
          className="dashboard-main-content"
          data-testid="analytics-charts-section"
        >
          <ChartsSection
            campaigns={campaigns}
            analyticsSummary={analyticsSummary}
            onDrillDown={handleCampaignDrillDown}
          />
        </section>

        {/* Campaign List Section */}
        <section
          className="dashboard-sidebar"
          data-testid="campaign-list-section"
        >
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Campaign Performance</h3>
              <span className="text-sm text-gray-600">
                {campaigns.length} campaigns
              </span>
            </div>

            <CampaignTable
              campaigns={campaigns}
              selectedCampaigns={selectedCampaigns}
              onSelectionChange={handleCampaignSelection}
              onCampaignClick={handleCampaignDrillDown}
              loading={loading}
            />
          </div>
        </section>
      </div>

      {/* Bulk Actions Bar (conditional) */}
      {selectedCampaigns.length > 0 && (
        <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg border border-gray-200 px-6 py-3">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">
              {selectedCampaigns.length} selected
            </span>
            <div className="flex space-x-2">
              <button
                className="btn btn-secondary text-sm"
                aria-label="Bulk actions"
              >
                <ChevronDown className="w-4 h-4 mr-1" />
                Bulk Actions
              </button>
              <button
                className="btn btn-secondary text-sm"
                aria-label="Export selected"
              >
                Export Selected
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Campaign Detail Modal */}
      {selectedCampaignId && (
        <CampaignDetailModal
          campaignId={selectedCampaignId}
          isOpen={isModalOpen}
          onClose={handleModalClose}
          data-testid="campaign-detail-modal"
        />
      )}
    </main>
  )
}

export default Dashboard