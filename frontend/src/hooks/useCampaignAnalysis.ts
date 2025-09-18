/**
 * useCampaignAnalysis Hook - Campaign Data Management and Analytics
 *
 * GREEN PHASE IMPLEMENTATION: Complete hook extracting complex state management
 * from the 346-line Dashboard component. Provides centralized campaign data fetching,
 * analytics computation, and filter management for system health analysis.
 *
 * Key Features:
 * - Parallel API calls for optimal performance
 * - Comprehensive error handling and recovery
 * - Memoized computed metrics for performance
 * - Filter state management with automatic refetching
 * - System health analysis for investigation workflows
 */

import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { Campaign, AnalyticsSummary, CampaignFilters, SystemHealthMetrics } from '@/types'
import { campaignApi, analyticsApi, apiUtils } from '@/lib/api'
import { calculateSystemHealthMetrics, getCampaignsRequiringAttention } from '@/lib/fulfillment'

// Interface for hook return value
export interface UseCampaignAnalysisReturn {
  campaigns: Campaign[]
  analyticsSummary: AnalyticsSummary | null
  loading: boolean
  error: string | null
  filters: CampaignFilters
  setFilters: (filters: Partial<CampaignFilters>) => void
  computedMetrics: {
    systemHealthMetrics: SystemHealthMetrics
    campaignsRequiringAttention: Campaign[]
  }
}

// Default filter state
const DEFAULT_FILTERS: CampaignFilters = {
  type: 'all',
  status: 'all',
  fulfillment_status: 'all',
  search: '',
}

/**
 * Custom hook for campaign analysis and data management
 *
 * GREEN PHASE: Complete implementation making all tests pass
 * Extracts 8 useState variables from Dashboard component
 */
export const useCampaignAnalysis = (
  initialFilters?: CampaignFilters
): UseCampaignAnalysisReturn => {
  // State management - replaces multiple useState in Dashboard
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [analyticsSummary, setAnalyticsSummary] = useState<AnalyticsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<CampaignFilters>({
    ...DEFAULT_FILTERS,
    ...initialFilters,
  })

  // Ref to track if component is mounted (prevents memory leaks)
  const isMountedRef = useRef(true)

  // Ref to track previous data for error recovery
  const previousDataRef = useRef<{
    campaigns: Campaign[]
    analyticsSummary: AnalyticsSummary | null
  }>({ campaigns: [], analyticsSummary: null })

  /**
   * Fetch campaign and analytics data in parallel for optimal performance
   * Implements error handling and data preservation patterns
   */
  const fetchData = useCallback(async (currentFilters: CampaignFilters) => {
    if (!isMountedRef.current) return

    setLoading(true)
    setError(null)

    try {
      // Parallel API calls for better UX - matches test expectations
      const [campaignsResponse, analyticsResponse] = await Promise.allSettled([
        campaignApi.getCampaigns(currentFilters),
        analyticsApi.getSummary(),
      ])

      if (!isMountedRef.current) return

      // Handle campaigns data
      if (campaignsResponse.status === 'fulfilled') {
        setCampaigns(campaignsResponse.value.data)
        previousDataRef.current.campaigns = campaignsResponse.value.data
      } else {
        // Preserve previous data on error - matches test expectations
        const errorMessage = apiUtils.parseApiError(campaignsResponse.reason)
        setError(errorMessage)
        console.warn('Campaigns API failed, preserving previous data:', errorMessage)
      }

      // Handle analytics data
      if (analyticsResponse.status === 'fulfilled') {
        setAnalyticsSummary(analyticsResponse.value)
        previousDataRef.current.analyticsSummary = analyticsResponse.value
      } else {
        // Partial failure handling - campaigns succeed, analytics fail
        const errorMessage = apiUtils.parseApiError(analyticsResponse.reason)
        setError(errorMessage)
        console.warn('Analytics API failed:', errorMessage)
      }

    } catch (error) {
      if (!isMountedRef.current) return

      const errorMessage = apiUtils.parseApiError(error)
      setError(errorMessage)
      console.error('Data fetching failed:', error)
    } finally {
      if (isMountedRef.current) {
        setLoading(false)
      }
    }
  }, [])

  // Filter management with automatic refetching - replaces Dashboard filter logic
  const setFilters = useCallback((newFilters: Partial<CampaignFilters>) => {
    setFiltersState(prev => {
      const updatedFilters = { ...prev, ...newFilters }

      // Trigger refetch with new filters - matches test expectations
      fetchData(updatedFilters)

      return updatedFilters
    })
  }, [fetchData])

  // Initial data fetching on mount
  useEffect(() => {
    fetchData(filters)

    // Cleanup function
    return () => {
      isMountedRef.current = false
    }
  }, []) // Only on mount - fetchData handles filter changes

  // Computed metrics with performance optimization - replaces Dashboard calculations
  const computedMetrics = useMemo(() => {
    // Return default metrics if no campaigns (handles empty data scenario)
    if (campaigns.length === 0) {
      return {
        systemHealthMetrics: {
          overall_system_health: 'healthy' as const,
          capacity_utilization: 0,
          average_fulfillment_rate: 0,
          campaigns_requiring_attention: 0,
          projected_completion_accuracy: 0,
          trend_indicators: {
            fulfillment_trend: 'stable' as const,
            capacity_trend: 'stable' as const,
            performance_momentum: 0,
          },
        },
        campaignsRequiringAttention: [],
      }
    }

    // Calculate system health metrics using fulfillment analysis
    const systemHealthMetrics = calculateSystemHealthMetrics(campaigns)
    const campaignsRequiringAttention = getCampaignsRequiringAttention(campaigns)

    return {
      systemHealthMetrics,
      campaignsRequiringAttention,
    }
  }, [campaigns]) // Recalculate when campaigns change

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false
    }
  }, [])

  return {
    campaigns,
    analyticsSummary,
    loading,
    error,
    filters,
    setFilters,
    computedMetrics,
  }
}