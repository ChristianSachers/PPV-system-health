/**
 * API Types for PPV System Health Monitor
 *
 * Core types focused on impression delivery fulfillment analysis
 * Primary metric: (delivered_impressions / impression_goal) × 100%
 */

// Core Campaign Types
export interface Campaign {
  id: string
  name: string
  campaign_type: 'campaign' | 'deal'
  is_running: boolean
  runtime_start: string | null  // ISO date string or null for ASAP
  runtime_end: string           // ISO date string
  impression_goal: number       // INTEGER (1 to 2,000,000,000)
  budget_eur: number
  cpm_eur: number
  buyer: string
  created_at: string           // ISO date string

  // Calculated fulfillment fields (computed by backend)
  fulfillment_percentage?: number
  delivered_impressions?: number

  // Performance metrics for detailed analysis
  performance_metrics?: PerformanceMetrics
}

// Performance Metrics for System Health Analysis
export interface PerformanceMetrics {
  impressions_delivered: number
  budget_spent: number
  days_remaining: number
  projected_completion: number  // 0.0 to 1.0 (percentage as decimal)
  daily_delivery_rate?: number
  expected_completion_date?: string
  health_status?: 'healthy' | 'at_risk' | 'underperforming'
}

// Fulfillment Analysis Types
export type FulfillmentStatus = 'excellent' | 'good' | 'warning' | 'critical'

export interface FulfillmentAnalysis {
  campaign_id: string
  fulfillment_percentage: number
  status: FulfillmentStatus
  variance_from_goal: number        // Positive or negative difference
  expected_completion: number       // Projected final fulfillment %
  recommendation: string
}

// Analytics and Dashboard Types
export interface AnalyticsSummary {
  total_campaigns: number
  total_deals: number
  overall_fulfillment_rate: number

  // Budget analysis
  total_budget_eur: number
  budget_spent_eur: number
  budget_remaining_eur: number

  // Impression analysis
  total_impression_goal: number
  total_impressions_delivered: number

  // Performance distribution
  fulfillment_distribution: {
    excellent: number    // Count of campaigns ≥100%
    good: number        // Count of campaigns 98-99.9%
    warning: number     // Count of campaigns 95-98%
    critical: number    // Count of campaigns <95%
  }

  // System health indicators
  system_health_score: number      // 0-100 composite score
  campaigns_at_risk: number        // Count needing attention
  underperforming_campaigns: Campaign[]
}

// Chart Data Types for Visualization
export interface ChartDataPoint {
  name: string
  value: number
  percentage?: number
  status?: FulfillmentStatus
}

export interface TimeSeriesPoint {
  date: string           // ISO date string
  impressions: number
  budget_spent: number
  fulfillment_rate: number
  campaign_count: number
}

// Filter and Search Types
export interface CampaignFilters {
  type?: 'campaign' | 'deal' | 'all'
  status?: 'running' | 'completed' | 'all'
  fulfillment_status?: FulfillmentStatus | 'all'
  search?: string
  date_range?: {
    start: string      // ISO date string
    end: string        // ISO date string
  }
}

// Upload and File Processing Types
export interface UploadResult {
  success: boolean
  message: string
  campaigns_processed?: number
  campaigns_created?: number
  campaigns_updated?: number
  errors?: ValidationError[]
}

export interface ValidationError {
  row: number
  field: string
  value: any
  message: string
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
  timestamp: string
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
  filters_applied?: CampaignFilters
}

// Error Types
export interface ApiError {
  message: string
  code?: string
  details?: any
  timestamp: string
  status?: number
}

// Modal and UI State Types
export interface ModalState {
  isOpen: boolean
  campaignId?: string
  type?: 'detail' | 'edit' | 'upload'
}

export interface UIState {
  loading: boolean
  error: ApiError | null
  lastUpdated: string | null
}

// Drill-down and Investigation Types
export interface DrillDownData {
  campaign: Campaign
  fulfillment_analysis: FulfillmentAnalysis
  historical_performance: TimeSeriesPoint[]
  related_campaigns?: Campaign[]
  root_cause_indicators?: {
    delivery_issues: boolean
    budget_constraints: boolean
    targeting_problems: boolean
    system_bottlenecks: boolean
  }
}