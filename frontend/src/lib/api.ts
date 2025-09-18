/**
 * API Client for PPV System Health Monitor
 *
 * Handles all backend API communication with proper error handling,
 * type safety, and fulfillment analysis focus.
 */

import {
  Campaign,
  AnalyticsSummary,
  CampaignFilters,
  ApiResponse,
  PaginatedResponse,
  UploadResult,
  DrillDownData,
  FulfillmentAnalysis,
  TimeSeriesPoint,
  ApiError,
} from '@/types'

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

// Custom error class for API errors
export class ApiClientError extends Error {
  public status: number
  public code?: string
  public details?: any

  constructor(message: string, status: number, code?: string, details?: any) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
    this.code = code
    this.details = details
  }
}

// HTTP Client with error handling
class HttpClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new ApiClientError(
          errorData.message || `HTTP ${response.status}`,
          response.status,
          errorData.code,
          errorData.details
        )
      }

      return await response.json()
    } catch (error) {
      if (error instanceof ApiClientError) {
        throw error
      }

      // Network or other errors
      throw new ApiClientError(
        error instanceof Error ? error.message : 'Network error',
        0,
        'NETWORK_ERROR'
      )
    }
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const searchParams = params ? new URLSearchParams(params).toString() : ''
    const url = searchParams ? `${endpoint}?${searchParams}` : endpoint
    return this.request<T>(url, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  async postFormData<T>(endpoint: string, formData: FormData): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: formData,
      headers: {}, // Don't set Content-Type for FormData
    })
  }
}

// Initialize HTTP client
const httpClient = new HttpClient(API_BASE_URL)

/**
 * Campaign API Service
 * Handles campaign CRUD operations and fulfillment analysis
 */
export const campaignApi = {
  /**
   * Get all campaigns with optional filtering
   * Supports system health analysis filtering
   */
  async getCampaigns(filters?: CampaignFilters): Promise<PaginatedResponse<Campaign>> {
    const params: Record<string, string> = {}

    if (filters?.type && filters.type !== 'all') {
      params.type = filters.type
    }
    if (filters?.status && filters.status !== 'all') {
      params.status = filters.status
    }
    if (filters?.fulfillment_status && filters.fulfillment_status !== 'all') {
      params.fulfillment_status = filters.fulfillment_status
    }
    if (filters?.search) {
      params.search = filters.search
    }
    if (filters?.date_range) {
      params.start_date = filters.date_range.start
      params.end_date = filters.date_range.end
    }

    return await httpClient.get<PaginatedResponse<Campaign>>('/campaigns', params)
  },

  /**
   * Get detailed campaign information for drill-down analysis
   */
  async getCampaignDetail(id: string): Promise<DrillDownData> {
    return await httpClient.get<DrillDownData>(`/campaigns/${id}`)
  },

  /**
   * Create new campaign
   */
  async createCampaign(campaign: Omit<Campaign, 'id' | 'created_at'>): Promise<Campaign> {
    const response = await httpClient.post<ApiResponse<Campaign>>('/campaigns', campaign)
    return response.data
  },

  /**
   * Update existing campaign
   */
  async updateCampaign(id: string, updates: Partial<Campaign>): Promise<Campaign> {
    const response = await httpClient.put<ApiResponse<Campaign>>(`/campaigns/${id}`, updates)
    return response.data
  },

  /**
   * Delete campaign
   */
  async deleteCampaign(id: string): Promise<void> {
    await httpClient.delete<ApiResponse<void>>(`/campaigns/${id}`)
  },

  /**
   * Upload XLSX file for campaign data processing
   */
  async uploadCampaigns(file: File): Promise<UploadResult> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await httpClient.postFormData<ApiResponse<UploadResult>>(
      '/campaigns/upload',
      formData
    )
    return response.data
  },
}

/**
 * Analytics API Service
 * Handles fulfillment analysis and system health metrics
 */
export const analyticsApi = {
  /**
   * Get dashboard summary with fulfillment metrics
   */
  async getSummary(): Promise<AnalyticsSummary> {
    const response = await httpClient.get<ApiResponse<AnalyticsSummary>>('/campaigns/analytics/summary')
    return response.data
  },

  /**
   * Get performance insights for optimization
   */
  async getPerformanceInsights(filters?: CampaignFilters): Promise<{
    underperforming_campaigns: Campaign[]
    optimization_recommendations: string[]
    system_health_score: number
  }> {
    const params = filters ? this.filtersToParams(filters) : {}
    const response = await httpClient.get<ApiResponse<any>>(
      '/campaigns/analytics/performance',
      params
    )
    return response.data
  },

  /**
   * Get fulfillment analysis for specific campaigns
   */
  async getFulfillmentAnalysis(campaignIds: string[]): Promise<FulfillmentAnalysis[]> {
    const response = await httpClient.post<ApiResponse<FulfillmentAnalysis[]>>(
      '/campaigns/analytics/fulfillment',
      { campaign_ids: campaignIds }
    )
    return response.data
  },

  /**
   * Get time series data for trend analysis
   */
  async getTimeSeriesData(
    dateRange: { start: string; end: string },
    granularity: 'daily' | 'weekly' | 'monthly' = 'daily'
  ): Promise<TimeSeriesPoint[]> {
    const response = await httpClient.get<ApiResponse<TimeSeriesPoint[]>>(
      '/campaigns/analytics/timeseries',
      {
        start_date: dateRange.start,
        end_date: dateRange.end,
        granularity,
      }
    )
    return response.data
  },

  /**
   * Helper method to convert filters to API parameters
   */
  private filtersToParams(filters: CampaignFilters): Record<string, string> {
    const params: Record<string, string> = {}

    if (filters.type && filters.type !== 'all') {
      params.type = filters.type
    }
    if (filters.status && filters.status !== 'all') {
      params.status = filters.status
    }
    if (filters.fulfillment_status && filters.fulfillment_status !== 'all') {
      params.fulfillment_status = filters.fulfillment_status
    }
    if (filters.search) {
      params.search = filters.search
    }
    if (filters.date_range) {
      params.start_date = filters.date_range.start
      params.end_date = filters.date_range.end
    }

    return params
  },
}

/**
 * Utility Functions for API Client
 */
export const apiUtils = {
  /**
   * Calculate fulfillment status based on percentage
   */
  getFulfillmentStatus(percentage: number): 'excellent' | 'good' | 'warning' | 'critical' {
    if (percentage >= 100) return 'excellent'
    if (percentage >= 98) return 'good'
    if (percentage >= 95) return 'warning'
    return 'critical'
  },

  /**
   * Format currency for display
   */
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  },

  /**
   * Format large numbers (impressions)
   */
  formatNumber(num: number): string {
    if (num >= 1000000000) {
      return (num / 1000000000).toFixed(1) + 'B'
    }
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  },

  /**
   * Format percentage for display
   */
  formatPercentage(percentage: number, decimals: number = 1): string {
    return `${percentage.toFixed(decimals)}%`
  },

  /**
   * Parse API error for user-friendly display
   */
  parseApiError(error: unknown): string {
    if (error instanceof ApiClientError) {
      return error.message
    }
    if (error instanceof Error) {
      return error.message
    }
    return 'An unexpected error occurred'
  },

  /**
   * Check if campaign runtime is ASAP
   */
  isAsapCampaign(campaign: Campaign): boolean {
    return campaign.runtime_start === null || campaign.runtime_start === 'ASAP'
  },

  /**
   * Calculate days remaining for campaign
   */
  getDaysRemaining(endDate: string): number {
    const end = new Date(endDate)
    const now = new Date()
    const diffTime = end.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return Math.max(0, diffDays)
  },
}

// Export default API client
export default {
  campaigns: campaignApi,
  analytics: analyticsApi,
  utils: apiUtils,
}