/**
 * DashboardErrorBoundary Component - Analytical Error Handling for Dashboard Components
 *
 * Educational Error Boundary Pattern: This component demonstrates analytical dashboard
 * error handling that preserves user context and provides meaningful recovery workflows.
 * Unlike generic error boundaries, this focuses on maintaining analytical value during failures.
 *
 * Key Features:
 * 1. Catches JavaScript rendering errors in dashboard components
 * 2. Preserves analytical context (campaigns, filters, analysis state)
 * 3. Provides contextual recovery options based on error type
 * 4. Logs errors with analytical context for debugging
 * 5. Offers alternative analysis workflows during failures
 *
 * Integration Points:
 * - Works alongside useCampaignAnalysis hook (API errors)
 * - Reuses existing ErrorMessage component patterns
 * - Coordinates with dashboard section components
 * - Supports granular error boundary placement
 */

import React, { Component, ReactNode } from 'react'
import { Campaign, SystemHealthMetrics, AnalyticsSummary } from '@/types'
import { AlertCircle, RefreshCw, Download, RotateCcw, Activity, Table } from 'lucide-react'

// Props interface for DashboardErrorBoundary
export interface DashboardErrorBoundaryProps {
  children: ReactNode
  section?: 'summary' | 'charts' | 'table' | 'filters'
  fallbackStrategy?: 'preserve-data' | 'minimal-ui' | 'full-refresh'
  analyticalContext?: {
    currentCampaigns?: Campaign[]
    activeFilters?: any
    analysisView?: string
    systemHealthMetrics?: SystemHealthMetrics
  }
  currentFilters?: any
  preserveAnalyticalState?: boolean
  onRefreshDashboard?: () => void
  onExportData?: (data: any[]) => void
  availableData?: any[]
  userRole?: 'product-manager' | 'analyst' | 'technical-user'
}

// Error boundary state interface
interface DashboardErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: any
  retryCount: number
}

/**
 * DashboardErrorBoundary - RED PHASE STUB
 *
 * This class component stub provides the basic error boundary structure
 * but does not implement the actual error catching and handling logic.
 * This ensures that all tests fail appropriately during the RED phase.
 */
class DashboardErrorBoundary extends Component<
  DashboardErrorBoundaryProps,
  DashboardErrorBoundaryState
> {
  constructor(props: DashboardErrorBoundaryProps) {
    super(props)

    // Initialize state - RED PHASE: basic structure only
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    }
  }

  /**
   * getDerivedStateFromError - Core Error Boundary Implementation
   *
   * This static method catches JavaScript errors during the render phase
   * and updates component state to trigger fallback UI rendering.
   */
  static getDerivedStateFromError(error: Error): Partial<DashboardErrorBoundaryState> {
    // Immediately update state to show error UI
    return {
      hasError: true,
      error
    }
  }

  /**
   * componentDidCatch - Error Logging and Context Preservation
   *
   * This lifecycle method handles error logging with analytical context
   * and performs any necessary cleanup or context preservation.
   */
  componentDidCatch(error: Error, errorInfo: any): void {
    // Update state with complete error information
    this.setState({
      hasError: true,
      error,
      errorInfo
    })

    // Log error with analytical context
    this.logErrorWithContext(error, errorInfo)

    // Preserve analytical state if requested
    if (this.props.preserveAnalyticalState) {
      // Context is already preserved in props, no additional action needed
      console.info('Analytical state preserved during error boundary activation')
    }
  }

  /**
   * handleRetry - Component Recovery Functionality
   *
   * Attempts to recover from the error by resetting error boundary state
   * and allowing child components to re-render.
   */
  private handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: this.state.retryCount + 1
    })

    console.info('Dashboard error boundary retry attempted', {
      retryCount: this.state.retryCount + 1,
      section: this.props.section
    })
  }

  /**
   * handleRefreshDashboard - Full Dashboard Recovery
   *
   * Triggers a complete dashboard refresh while preserving user context.
   * Used for persistent errors that component retry cannot resolve.
   */
  private handleRefreshDashboard = (): void => {
    if (this.props.onRefreshDashboard) {
      this.props.onRefreshDashboard()
    }

    // Reset error boundary state after triggering refresh
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    })

    console.info('Dashboard refresh triggered from error boundary', {
      section: this.props.section,
      analyticalContext: !!this.props.analyticalContext
    })
  }

  /**
   * handleExportData - Emergency Data Export
   *
   * Provides data export functionality during error states to ensure
   * analytical work can continue even when visualization fails.
   */
  private handleExportData = (): void => {
    if (this.props.onExportData && this.props.availableData) {
      this.props.onExportData(this.props.availableData)
    } else if (this.props.analyticalContext?.currentCampaigns) {
      // Export available campaign data if no specific data provided
      if (this.props.onExportData) {
        this.props.onExportData(this.props.analyticalContext.currentCampaigns)
      }
    }

    console.info('Data export triggered from error boundary', {
      section: this.props.section,
      dataAvailable: !!(this.props.availableData || this.props.analyticalContext?.currentCampaigns)
    })
  }

  /**
   * logErrorWithContext - Enhanced Error Logging for Analytics
   *
   * Logs errors with comprehensive analytical context to support debugging
   * and improve error handling in dashboard components.
   */
  private logErrorWithContext(error: Error, errorInfo: any): void {
    const contextualErrorLog = {
      type: 'dashboard-error-boundary',
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name
      },
      errorInfo,
      analyticalContext: this.props.analyticalContext,
      section: this.props.section,
      userRole: this.props.userRole,
      timestamp: new Date().toISOString(),
      retryCount: this.state.retryCount,
      preserveAnalyticalState: this.props.preserveAnalyticalState
    }

    // Console logging for development
    console.error('DashboardErrorBoundary caught error', contextualErrorLog)

    // In production, this would integrate with monitoring service
    // logToMonitoringService(contextualErrorLog)
  }

  /**
   * getErrorType - Determine Error Category for Contextual Messaging
   *
   * Analyzes error message and context to categorize the type of error
   * and provide appropriate recovery suggestions.
   */
  private getErrorType(error: Error): string {
    const message = error.message.toLowerCase()

    if (message.includes('failed to process') && message.includes('analytics')) {
      return 'data-processing'
    } else if (message.includes('chart rendering') || message.includes('cannot read property')) {
      return 'chart-rendering'
    } else if (message.includes('maximum call stack') || message.includes('rangeerror')) {
      return 'memory-error'
    } else {
      return 'generic'
    }
  }

  /**
   * getContextualErrorMessage - Generate User-Friendly Error Messages
   *
   * Creates contextual error messages based on error type and dashboard section.
   */
  private getContextualErrorMessage(errorType: string): { title: string; message: string; suggestion: string } {
    const sectionText = this.props.section ? ` in ${this.props.section} section` : ''

    switch (errorType) {
      case 'data-processing':
        return {
          title: 'Data Processing Issue',
          message: `There was a problem processing the campaign data${sectionText}.`,
          suggestion: 'Try refreshing or export raw data for external analysis.'
        }
      case 'chart-rendering':
        return {
          title: 'Charts Temporarily Unavailable',
          message: `Charts${sectionText} are temporarily unavailable due to a rendering issue.`,
          suggestion: 'View data in table format or try refreshing the dashboard.'
        }
      case 'memory-error':
        return {
          title: 'Performance Issue',
          message: `Dashboard${sectionText} is experiencing performance issues.`,
          suggestion: 'Try filtering to reduce data size or refresh the dashboard.'
        }
      default:
        return {
          title: 'Something Went Wrong',
          message: `A component${sectionText} encountered an unexpected error.`,
          suggestion: 'Try refreshing or contact support if the problem persists.'
        }
    }
  }

  /**
   * renderFallbackUI - Error Boundary Fallback Interface
   *
   * Renders contextual error UI with recovery options based on error type
   * and available analytical context.
   */
  private renderFallbackUI(): ReactNode {
    const { error } = this.state
    const { section, analyticalContext, currentFilters, availableData } = this.props

    if (!error) return null

    const errorType = this.getErrorType(error)
    const { title, message, suggestion } = this.getContextualErrorMessage(errorType)
    const hasPartialData = !!(availableData?.length || analyticalContext?.currentCampaigns?.length)

    return (
      <div
        className="p-6 bg-red-50 border border-red-200 rounded-lg"
        data-testid="error-boundary-fallback"
        role="alert"
      >
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />

          <div className="flex-1 min-w-0">
            <h3 className="text-base font-medium text-red-800 mb-2">
              {title}
            </h3>
            <p className="text-sm text-red-700 mb-2">
              {message}
            </p>
            <p className="text-sm text-red-600 mb-4">
              {suggestion}
            </p>

            {/* Show preserved context info */}
            {currentFilters && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
                <p className="text-sm text-blue-800">
                  <strong>Current filters preserved:</strong> {JSON.stringify(currentFilters)}
                </p>
              </div>
            )}

            {/* Show partial data availability */}
            {hasPartialData && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-green-600" />
                  <p className="text-sm text-green-800">
                    <strong>Good news:</strong> Campaign data is still available for basic analysis.
                  </p>
                </div>
              </div>
            )}

            {/* Recovery Actions */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={this.handleRetry}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
                data-testid="retry-button"
              >
                <RotateCcw className="w-4 h-4" />
                Retry
              </button>

              {this.props.onRefreshDashboard && (
                <button
                  onClick={this.handleRefreshDashboard}
                  className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh Dashboard
                </button>
              )}

              {hasPartialData && (
                <button
                  onClick={this.handleExportData}
                  className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Export Data
                </button>
              )}

              {/* Alternative Analysis Options */}
              {hasPartialData && (
                <>
                  <button
                    className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
                  >
                    <Table className="w-4 h-4" />
                    View Data Table
                  </button>
                  <button
                    className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors"
                  >
                    <Activity className="w-4 h-4" />
                    Simple Summary View
                  </button>
                </>
              )}
            </div>

            {/* Technical Details for Development */}
            {process.env.NODE_ENV === 'development' && (
              <details className="mt-4">
                <summary className="text-xs text-gray-600 cursor-pointer">Technical Details</summary>
                <pre className="mt-2 text-xs text-gray-500 bg-gray-100 p-2 rounded overflow-auto">
                  {error.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      </div>
    )
  }

  /**
   * render - Main Render Method with Error Boundary Logic
   *
   * Renders either the error fallback UI or the wrapped children components
   * based on error boundary state.
   */
  render(): ReactNode {
    if (this.state.hasError) {
      return this.renderFallbackUI()
    }

    // Normal rendering - wrap children with key to force re-render on retry
    return (
      <React.Fragment key={this.state.retryCount}>
        {this.props.children}
      </React.Fragment>
    )
  }
}

export default DashboardErrorBoundary

/**
 * RED PHASE IMPLEMENTATION STATUS:
 *
 * ✓ Component can be imported (prevents import errors in tests)
 * ✓ TypeScript interfaces defined (provides development structure)
 * ✓ Basic class component structure exists
 * ✗ Error catching not implemented (getDerivedStateFromError returns empty)
 * ✗ Error handling not implemented (componentDidCatch doesn't update state)
 * ✗ Fallback UI not implemented (render always shows children)
 * ✗ Recovery actions not implemented (methods exist but don't work)
 * ✗ Analytical context logging not implemented
 * ✗ Integration with existing components not implemented
 *
 * EXPECTED TEST RESULTS:
 * - Import tests: ✓ PASS (component exists)
 * - Error catching tests: ✗ FAIL (errors not caught)
 * - Fallback UI tests: ✗ FAIL (error UI never shown)
 * - Recovery action tests: ✗ FAIL (methods don't work)
 * - Context logging tests: ✗ FAIL (only console.warn)
 * - Integration tests: ✗ FAIL (no actual integration)
 *
 * This is exactly what we want for RED phase TDD!
 */