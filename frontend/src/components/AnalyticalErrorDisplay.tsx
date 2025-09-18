/**
 * AnalyticalErrorDisplay Component - Comprehensive Data Error Handling for Analytical Workflows
 *
 * Educational Error Display Pattern: This component demonstrates data-centric error handling
 * specifically designed for analytical dashboard failures. Unlike generic error messages,
 * this focuses on preserving analytical value and providing meaningful alternatives.
 *
 * Key Features:
 * 1. Context-aware error messaging based on error type and user role
 * 2. Partial data availability communication and visualization
 * 3. Alternative analysis suggestion mechanisms for continued productivity
 * 4. Progressive disclosure of technical details for different user types
 * 5. Integration with analytical workflow context for relevant guidance
 * 6. Data export functionality to ensure work continuity during errors
 *
 * Component Distinction:
 * - DashboardErrorBoundary: Catches JavaScript rendering errors
 * - AnalyticalErrorDisplay: Displays data loading/processing errors with context
 *
 * Integration Points:
 * - useCampaignAnalysis hook error states
 * - Existing ErrorMessage component patterns with enhanced functionality
 * - Dashboard recovery workflows and alternative analysis paths
 */

import React, { useState } from 'react'
import { Campaign, AnalyticsSummary, BaseComponentProps } from '@/types'
import { AlertCircle, AlertTriangle, WifiOff, Server, Shield, RefreshCw, Download, Table, Activity, ChevronDown, ChevronUp, FileText, HelpCircle } from 'lucide-react'

// Error type definitions for analytical errors
export interface AnalyticalError {
  type: 'api-error' | 'data-parsing' | 'calculation-error' | 'authentication' | 'network'
  message: string
  code: string
  retryable: boolean
  partialData: boolean
  availableData?: any[]
}

// Data quality issue interface
export interface DataQualityIssue {
  field: string
  issue: string
  affectedRecords: number
}

// Alternative analysis option interface
export interface AlternativeAnalysisOption {
  type: string
  label: string
  action: () => void
}

// Workflow context interface
export interface WorkflowContext {
  type: 'fulfillment-analysis' | 'budget-planning' | 'performance-investigation'
  data: any
}

// Technical details interface
export interface TechnicalDetails {
  stackTrace?: string
  errorCode?: string
  timestamp?: string
  affectedComponents?: string[]
}

// Props interface for AnalyticalErrorDisplay
export interface AnalyticalErrorDisplayProps extends BaseComponentProps {
  error: AnalyticalError
  partialData?: any[]
  alternativeAnalysisOptions?: AlternativeAnalysisOption[]
  userRole?: 'product-manager' | 'analyst' | 'technical-user'
  workflowContext?: WorkflowContext
  currentFilters?: any
  dataQualityIssues?: DataQualityIssue[]
  technicalDetails?: TechnicalDetails
  onRetry?: () => Promise<{ success: boolean }>
  onExportData?: (data: any[], format: string) => void
  onNavigateToTable?: (options: any) => void
  onUpdateFilters?: (filters: any) => void
}

/**
 * AnalyticalErrorDisplay - Comprehensive Data Error Handling Component
 *
 * This functional component provides sophisticated error display and recovery
 * functionality specifically designed for analytical dashboard workflows.
 */
const AnalyticalErrorDisplay: React.FC<AnalyticalErrorDisplayProps> = ({
  error,
  partialData,
  alternativeAnalysisOptions,
  userRole = 'product-manager',
  workflowContext,
  currentFilters,
  dataQualityIssues,
  technicalDetails,
  onRetry,
  onExportData,
  onNavigateToTable,
  onUpdateFilters,
  className = '',
  'data-testid': testId = 'analytical-error-display'
}) => {
  // State for progressive disclosure
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false)
  const [isRetrying, setIsRetrying] = useState(false)
  const [retryStatus, setRetryStatus] = useState<'idle' | 'success' | 'failed'>('idle')

  /**
   * getErrorIcon - Error Type Icon Selection
   *
   * Returns appropriate icon component based on error type for visual clarity.
   */
  const getErrorIcon = (errorType: string) => {
    const iconProps = { className: "w-5 h-5 flex-shrink-0 mt-0.5" }

    switch (errorType) {
      case 'api-error':
        return <Server {...iconProps} className={`${iconProps.className} text-red-600`} data-testid="error-icon-api-error" />
      case 'network':
        return <WifiOff {...iconProps} className={`${iconProps.className} text-orange-600`} data-testid="error-icon-network" />
      case 'authentication':
        return <Shield {...iconProps} className={`${iconProps.className} text-purple-600`} data-testid="error-icon-authentication" />
      case 'data-parsing':
        return <AlertTriangle {...iconProps} className={`${iconProps.className} text-yellow-600`} data-testid="error-icon-data-parsing" />
      case 'calculation-error':
        return <AlertCircle {...iconProps} className={`${iconProps.className} text-blue-600`} data-testid="error-icon-calculation-error" />
      default:
        return <AlertCircle {...iconProps} className={`${iconProps.className} text-red-600`} data-testid="error-icon-generic" />
    }
  }

  /**
   * getErrorMessage - Role-Based Error Messaging
   *
   * Generates contextual error messages based on error type and user role.
   */
  const getErrorMessage = (error: AnalyticalError, userRole: string): string => {
    const messageMap: Record<string, Record<string, string>> = {
      'api-error': {
        'product-manager': 'There was an issue loading your campaign analysis',
        'analyst': 'Data processing error in fulfillment metrics calculation',
        'technical-user': `API Error: ${error.code} - ${error.message}`
      },
      'data-parsing': {
        'product-manager': 'Some campaign data contains formatting issues',
        'analyst': 'Data quality issues detected in campaign metrics',
        'technical-user': `Data Parsing Error: ${error.code} - ${error.message}`
      },
      'calculation-error': {
        'product-manager': 'Unable to calculate system health metrics',
        'analyst': 'Analytics calculation failed - partial results available',
        'technical-user': `Calculation Error: ${error.code} - ${error.message}`
      },
      'authentication': {
        'product-manager': 'Session expired - please log in again',
        'analyst': 'Authentication required to access analytical data',
        'technical-user': `Auth Error: ${error.code} - ${error.message}`
      },
      'network': {
        'product-manager': 'Network connection lost',
        'analyst': 'Unable to connect to analytics server',
        'technical-user': `Network Error: ${error.code} - ${error.message}`
      }
    }

    return messageMap[error.type]?.[userRole] || error.message
  }

  /**
   * getRecoveryActions - Context-Aware Recovery Suggestions
   *
   * Generates appropriate recovery actions based on error type and available data.
   */
  const getRecoveryActions = (error: AnalyticalError, partialData?: any[]): string[] => {
    const actionMap: Record<string, string[]> = {
      'api-error': ['Retry loading data', 'Check network connection', 'Use cached data if available'],
      'data-parsing': ['View available campaigns', 'Export partial data', 'Contact support with data details'],
      'authentication': ['Log in again', 'Contact administrator if problem persists'],
      'calculation-error': ['Try basic analysis view', 'Export raw data', 'Retry calculation'],
      'network': ['Check connection', 'Retry when online', 'Use cached data']
    }

    let actions = actionMap[error.type] || ['Try refreshing the page']

    // Add data-specific actions if partial data is available
    if (partialData?.length) {
      actions = [...actions, 'View available data', 'Export partial results']
    }

    return actions
  }

  /**
   * getWorkflowGuidance - Workflow-Specific Analytical Guidance
   *
   * Provides contextual guidance based on current analytical workflow.
   */
  const getWorkflowGuidance = (workflowContext?: WorkflowContext): string => {
    if (!workflowContext) return 'Try alternative analysis methods'

    switch (workflowContext.type) {
      case 'fulfillment-analysis':
        return 'Try analyzing fewer campaigns to isolate the data issue'
      case 'budget-planning':
        return 'Export available budget data to continue planning offline'
      case 'performance-investigation':
        return 'View individual campaign details to continue investigation'
      default:
        return 'Try alternative analysis methods'
    }
  }

  /**
   * handleRetry - Retry Functionality with Loading States
   *
   * Implements retry logic with proper loading states and error handling.
   */
  const handleRetry = async (): Promise<void> => {
    if (!onRetry) return

    setIsRetrying(true)
    setRetryStatus('idle')

    try {
      const result = await onRetry()
      if (result.success) {
        setRetryStatus('success')
      } else {
        setRetryStatus('failed')
      }
    } catch (error) {
      setRetryStatus('failed')
    } finally {
      setIsRetrying(false)
    }
  }

  /**
   * handleExportData - Data Export with Format Options
   *
   * Provides data export functionality for continued analysis.
   */
  const handleExportData = (format: string = 'csv'): void => {
    if (onExportData && partialData) {
      onExportData(partialData, format)
    }
  }

  /**
   * toggleTechnicalDetails - Progressive Disclosure Toggle
   *
   * Manages technical details visibility for different user needs.
   */
  const toggleTechnicalDetails = (): void => {
    setShowTechnicalDetails(prev => !prev)
  }

  // Render main component UI
  return (
    <div
      className={`analytical-error-display bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}
      data-testid={testId}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {getErrorIcon(error.type)}

        <div className="flex-1 min-w-0">
          {/* Error Header */}
          <h3 className="text-base font-medium text-red-800 mb-2">
            {getErrorMessage(error, userRole)}
          </h3>

          {/* Partial Data Status */}
          {partialData?.length && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-green-600" />
                <p className="text-sm text-green-800">
                  <strong>Partial data available:</strong> {partialData.length} campaign{partialData.length !== 1 ? 's' : ''} loaded successfully
                </p>
              </div>
              {partialData.slice(0, 2).map((item: any, index: number) => (
                <p key={index} className="text-xs text-green-700 mt-1">
                  • {item.name || `Campaign ${item.id}`}
                </p>
              ))}
              {partialData.length > 2 && (
                <p className="text-xs text-green-700 mt-1">
                  ... and {partialData.length - 2} more
                </p>
              )}
            </div>
          )}

          {/* Current Filters Context */}
          {currentFilters && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm text-blue-800">
                <strong>Current filters:</strong> {Object.entries(currentFilters).map(([key, value]) => `${key}: ${value}`).join(', ')}
              </p>
            </div>
          )}

          {/* Data Quality Issues */}
          {dataQualityIssues?.length && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
              <h4 className="text-sm font-medium text-yellow-800 mb-2">Data Quality Issues Detected</h4>
              <p className="text-sm text-yellow-700 mb-2">
                {dataQualityIssues.reduce((total, issue) => total + issue.affectedRecords, 0)} records affected
              </p>
              {dataQualityIssues.slice(0, 3).map((issue, index) => (
                <p key={index} className="text-xs text-yellow-700">
                  • {issue.field}: {issue.issue} ({issue.affectedRecords} records)
                </p>
              ))}
              {dataQualityIssues.length > 3 && (
                <button
                  onClick={toggleTechnicalDetails}
                  className="text-xs text-yellow-600 hover:text-yellow-800 mt-1"
                >
                  View all issues...
                </button>
              )}
            </div>
          )}

          {/* Workflow-Specific Guidance */}
          {workflowContext && (
            <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded">
              <p className="text-sm text-purple-800">
                <strong>Suggestion:</strong> {getWorkflowGuidance(workflowContext)}
              </p>
            </div>
          )}

          {/* Recovery Actions */}
          <div className="flex flex-wrap gap-2 mb-4">
            {error.retryable && onRetry && (
              <button
                onClick={handleRetry}
                disabled={isRetrying}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isRetrying ? 'animate-spin' : ''}`} />
                {isRetrying ? 'Retrying...' : 'Retry'}
              </button>
            )}

            {partialData?.length && onExportData && (
              <button
                onClick={() => handleExportData('csv')}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
              >
                <Download className="w-4 h-4" />
                Export Available Data
              </button>
            )}

            {partialData?.length && onNavigateToTable && (
              <button
                onClick={() => onNavigateToTable({ data: partialData, preserveFilters: true })}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
              >
                <Table className="w-4 h-4" />
                View in Table Format
              </button>
            )}
          </div>

          {/* Alternative Analysis Options */}
          {alternativeAnalysisOptions?.length && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-800 mb-2">Try these alternative analysis methods:</h4>
              <div className="flex flex-wrap gap-2">
                {alternativeAnalysisOptions.map((option, index) => (
                  <button
                    key={index}
                    onClick={option.action}
                    className="inline-flex items-center gap-2 px-3 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors"
                  >
                    <Activity className="w-4 h-4" />
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Retry Status */}
          {retryStatus !== 'idle' && (
            <div className={`mb-4 p-2 rounded ${retryStatus === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              <p className="text-sm">
                {retryStatus === 'success' ? 'Data loaded successfully!' : 'Retry failed. Please try again later.'}
              </p>
            </div>
          )}

          {/* Progressive Disclosure - Technical Details */}
          {technicalDetails && (
            <div className="mt-4">
              <button
                onClick={toggleTechnicalDetails}
                className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 focus:outline-none"
              >
                {showTechnicalDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                Show Technical Details
              </button>

              {showTechnicalDetails && (
                <div className="mt-2 p-3 bg-gray-100 border border-gray-200 rounded">
                  <div className="text-xs text-gray-700 space-y-2">
                    {technicalDetails.errorCode && (
                      <p><strong>Error Code:</strong> {technicalDetails.errorCode}</p>
                    )}
                    {technicalDetails.timestamp && (
                      <p><strong>Timestamp:</strong> {technicalDetails.timestamp}</p>
                    )}
                    {technicalDetails.affectedComponents?.length && (
                      <p><strong>Affected Components:</strong> {technicalDetails.affectedComponents.join(', ')}</p>
                    )}
                    {technicalDetails.stackTrace && (
                      <details className="mt-2">
                        <summary className="cursor-pointer">Stack Trace</summary>
                        <pre className="mt-1 text-xs bg-gray-200 p-2 rounded overflow-auto">
                          {technicalDetails.stackTrace}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AnalyticalErrorDisplay

/**
 * RED PHASE IMPLEMENTATION STATUS:
 *
 * ✓ Component can be imported (prevents import errors in tests)
 * ✓ TypeScript interfaces defined (provides development structure)
 * ✓ Basic functional component structure exists
 * ✓ Props are accepted and logged for debugging
 * ✗ Error type differentiation not implemented (shows placeholder)
 * ✗ Role-based messaging not implemented (generic message)
 * ✗ Recovery actions not implemented (empty array returned)
 * ✗ Partial data display not implemented (placeholder only)
 * ✗ Progressive disclosure not implemented (no state management)
 * ✗ Workflow-specific guidance not implemented (generic guidance)
 * ✗ Alternative analysis options not implemented (placeholder)
 * ✗ Data export functionality not implemented (no actual export)
 * ✗ Retry functionality not implemented (no actual retry)
 * ✗ Integration with existing components not implemented
 *
 * EXPECTED TEST RESULTS:
 * - Import tests: ✓ PASS (component exists)
 * - Error type display tests: ✗ FAIL (shows placeholder)
 * - Role-based messaging tests: ✗ FAIL (generic message)
 * - Recovery action tests: ✗ FAIL (no actions provided)
 * - Partial data tests: ✗ FAIL (no actual data display)
 * - Progressive disclosure tests: ✗ FAIL (no state management)
 * - Workflow context tests: ✗ FAIL (generic guidance)
 * - Data export tests: ✗ FAIL (no actual export)
 * - Retry functionality tests: ✗ FAIL (no actual retry)
 * - Integration tests: ✗ FAIL (no actual integration)
 *
 * This is exactly what we want for RED phase TDD!
 * Tests document the required behavior while implementation stubs ensure tests fail appropriately.
 */