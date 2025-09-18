/**
 * Utility Types and Re-exports for PPV System Health Monitor
 */

// Re-export all API types
export * from './api'

// Utility Types for Component Props
export interface BaseComponentProps {
  className?: string
  'data-testid'?: string
}

// Color Mapping for Fulfillment Status
export const FULFILLMENT_COLORS = {
  excellent: 'text-fulfillment-excellent bg-fulfillment-excellent/10 border-fulfillment-excellent/20',
  good: 'text-fulfillment-good bg-fulfillment-good/10 border-fulfillment-good/20',
  warning: 'text-fulfillment-warning bg-fulfillment-warning/10 border-fulfillment-warning/20',
  critical: 'text-fulfillment-critical bg-fulfillment-critical/10 border-fulfillment-critical/20',
} as const

// Fulfillment Status Thresholds
export const FULFILLMENT_THRESHOLDS = {
  EXCELLENT: 100,  // ≥100%
  GOOD: 98,       // 98-99.9%
  WARNING: 95,    // 95-98%
  CRITICAL: 0,    // <95%
} as const

// Chart Configuration Types
export interface ChartConfig {
  colors: string[]
  responsive: boolean
  animation: boolean
  tooltip: boolean
}

// Table Configuration Types
export interface TableColumn<T = any> {
  key: keyof T
  title: string
  width?: number | string
  sortable?: boolean
  render?: (value: any, record: T) => React.ReactNode
  className?: string
}

export interface TableProps<T = any> {
  columns: TableColumn<T>[]
  data: T[]
  loading?: boolean
  onRowClick?: (record: T) => void
  pagination?: {
    current: number
    pageSize: number
    total: number
    onChange: (page: number, pageSize: number) => void
  }
}

// Form Types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'date' | 'file'
  required?: boolean
  options?: { label: string; value: any }[]
  validation?: (value: any) => string | null
}

// Hook Return Types
export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
  refresh: () => void
}

export interface UsePaginatedState<T> extends UseApiState<T[]> {
  pagination: {
    current: number
    pageSize: number
    total: number
  }
  changePage: (page: number, pageSize?: number) => void
}

// Performance Analytics Types for System Health Insights
export interface SystemHealthMetrics {
  overall_system_health: 'healthy' | 'degraded' | 'critical'
  capacity_utilization: number        // 0-100 percentage
  average_fulfillment_rate: number    // 0-100 percentage
  campaigns_requiring_attention: number
  projected_completion_accuracy: number

  trend_indicators: {
    fulfillment_trend: 'improving' | 'stable' | 'declining'
    capacity_trend: 'increasing' | 'stable' | 'decreasing'
    performance_momentum: number      // -1 to 1 scale
  }
}

// Investigation Workflow Types
export interface InvestigationContext {
  selected_campaigns: string[]
  filter_criteria: CampaignFilters
  analysis_focus: 'performance' | 'capacity' | 'trends' | 'outliers'
  drill_down_path: string[]           // Track navigation path
}

// Export commonly used utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequireAtLeastOne<T, Keys extends keyof T = keyof T> =
  Pick<T, Exclude<keyof T, Keys>> &
  { [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>> }[Keys]

// Component Ref Types
export type ComponentRef<T = HTMLDivElement> = React.RefObject<T>

// Event Handler Types
export type ClickHandler<T = HTMLElement> = (event: React.MouseEvent<T>) => void
export type ChangeHandler<T = HTMLInputElement> = (event: React.ChangeEvent<T>) => void
export type SubmitHandler<T = HTMLFormElement> = (event: React.FormEvent<T>) => void