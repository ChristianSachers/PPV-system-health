/**
 * Campaign Detail Modal Component
 *
 * Drill-down modal for detailed campaign analysis and investigation.
 * Implements TDD specifications from CampaignDetailModal.test.tsx with focus on:
 * - Modal accessibility and keyboard navigation
 * - Detailed campaign metrics and timeline visualization
 * - Interactive elements for campaign management
 * - Mobile-responsive design
 */

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { createPortal } from 'react-dom'
import {
  X,
  Calendar,
  Target,
  TrendingUp,
  Edit,
  Play,
  Pause,
  Copy,
  Download,
  FileText
} from 'lucide-react'

import {
  Campaign,
  DrillDownData,
  BaseComponentProps,
  FulfillmentStatus
} from '@/types'
import {
  calculateFulfillmentPercentage,
  getFulfillmentStatus,
  getFulfillmentStatusClasses,
  getFulfillmentStatusLabel,
  analyzeCampaignPerformance
} from '@/lib/fulfillment'
import { campaignApi, apiUtils } from '@/lib/api'
import LoadingSpinner from './ui/LoadingSpinner'
import ErrorMessage from './ui/ErrorMessage'

interface CampaignDetailModalProps extends BaseComponentProps {
  campaignId: string
  isOpen: boolean
  onClose: () => void
}

const CampaignDetailModal: React.FC<CampaignDetailModalProps> = ({
  campaignId,
  isOpen,
  onClose,
  className = '',
  'data-testid': testId = 'campaign-detail-modal'
}) => {
  // State Management
  const [drillDownData, setDrillDownData] = useState<DrillDownData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)

  // Refs for focus management
  const modalRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)

  /**
   * Fetch campaign detail data
   */
  const fetchCampaignDetails = useCallback(async () => {
    if (!campaignId) return

    try {
      setLoading(true)
      setError(null)
      const data = await campaignApi.getCampaignDetail(campaignId)
      setDrillDownData(data)
    } catch (err) {
      const errorMessage = apiUtils.parseApiError(err)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [campaignId])

  /**
   * Handle ESC key press and focus management
   */
  useEffect(() => {
    if (!isOpen) return

    // Store current focus
    previousFocusRef.current = document.activeElement as HTMLElement

    // Focus modal
    setTimeout(() => {
      modalRef.current?.focus()
    }, 100)

    // ESC key handler
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleClose()
      }
    }

    // Focus trap handler
    const handleTab = (e: KeyboardEvent) => {
      if (e.key === 'Tab' && modalRef.current) {
        const focusableElements = modalRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        const firstElement = focusableElements[0] as HTMLElement
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }

    document.addEventListener('keydown', handleEsc)
    document.addEventListener('keydown', handleTab)

    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.removeEventListener('keydown', handleTab)
    }
  }, [isOpen])

  /**
   * Fetch data when modal opens
   */
  useEffect(() => {
    if (isOpen && campaignId) {
      fetchCampaignDetails()
    }
  }, [isOpen, campaignId, fetchCampaignDetails])

  /**
   * Handle modal close with focus restoration
   */
  const handleClose = useCallback(() => {
    onClose()
    // Restore focus
    setTimeout(() => {
      previousFocusRef.current?.focus()
    }, 100)
  }, [onClose])

  /**
   * Handle overlay click
   */
  const handleOverlayClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleClose()
    }
  }, [handleClose])

  /**
   * Handle campaign actions
   */
  const handlePauseCampaign = useCallback(() => {
    console.log('Pause campaign:', campaignId)
    // TODO: Implement pause functionality
  }, [campaignId])

  const handleDuplicateCampaign = useCallback(() => {
    console.log('Duplicate campaign:', campaignId)
    // TODO: Implement duplicate functionality
  }, [campaignId])

  const handleExportData = useCallback(() => {
    console.log('Export campaign data:', campaignId)
    // TODO: Implement export functionality
  }, [campaignId])

  const handleViewFullReport = useCallback(() => {
    console.log('View full report:', campaignId)
    // TODO: Implement full report navigation
  }, [campaignId])

  if (!isOpen) return null

  return createPortal(
    <div
      className="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={handleOverlayClick}
      data-testid="modal-overlay"
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className={`
          modal-content bg-white rounded-lg shadow-xl
          w-full max-w-4xl max-h-[90vh] overflow-auto
          mobile-fullscreen lg:max-w-4xl lg:mx-auto
          ${className}
        `}
        onClick={(e) => e.stopPropagation()}
        data-testid="modal-content"
        tabIndex={-1}
      >
        {/* Loading State */}
        {loading && (
          <div className="p-8">
            <LoadingSpinner
              message="Loading campaign details..."
              data-testid="modal-loading-spinner"
            />
          </div>
        )}

        {/* Error State */}
        {error && !drillDownData && (
          <div className="p-6">
            <ErrorMessage
              error={error}
              onRetry={fetchCampaignDetails}
              data-testid="error-message"
            />
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleClose}
                className="btn btn-secondary"
                aria-label="Close modal"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Campaign Details */}
        {drillDownData && (
          <>
            {/* Modal Header */}
            <header className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h1
                    id="modal-title"
                    className="text-xl font-semibold text-gray-900 truncate"
                    title={drillDownData.campaign.name}
                  >
                    {drillDownData.campaign.name}
                  </h1>
                  <div className="flex items-center space-x-4 mt-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        drillDownData.campaign.campaign_type === 'campaign'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-purple-100 text-purple-800'
                      }`}
                      data-testid="campaign-type-badge"
                    >
                      {drillDownData.campaign.campaign_type === 'campaign' ? 'Campaign' : 'Deal'}
                    </span>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        drillDownData.campaign.is_running
                          ? 'bg-green-100 text-green-800 status-running'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                      data-testid="campaign-status"
                    >
                      {drillDownData.campaign.is_running ? 'Running' : 'Completed'}
                    </span>
                  </div>
                </div>

                <button
                  onClick={handleClose}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                  aria-label="Close modal"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </header>

            {/* Modal Body */}
            <div className="px-6 py-6 space-y-6" data-testid="campaign-details">
              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Total Budget */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Total Budget</div>
                  <div className="text-2xl font-semibold text-gray-900" data-testid="total-budget">
                    {apiUtils.formatCurrency(drillDownData.campaign.budget_eur)}
                  </div>
                </div>

                {/* Budget Spent */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Budget Spent</div>
                  <div className="text-2xl font-semibold text-gray-900" data-testid="budget-spent">
                    {drillDownData.campaign.performance_metrics
                      ? apiUtils.formatCurrency(drillDownData.campaign.performance_metrics.budget_spent)
                      : 'N/A'
                    }
                  </div>
                </div>

                {/* Impression Goal */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Impression Goal</div>
                  <div className="text-2xl font-semibold text-gray-900" data-testid="impression-goal">
                    {apiUtils.formatNumber(drillDownData.campaign.impression_goal)}
                  </div>
                </div>

                {/* Impressions Delivered */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Delivered</div>
                  <div className="text-2xl font-semibold text-gray-900" data-testid="impressions-delivered">
                    {drillDownData.campaign.performance_metrics
                      ? apiUtils.formatNumber(drillDownData.campaign.performance_metrics.impressions_delivered)
                      : 'N/A'
                    }
                  </div>
                </div>

                {/* CPM */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">CPM</div>
                  <div className="text-2xl font-semibold text-gray-900" data-testid="cpm">
                    {apiUtils.formatCurrency(drillDownData.campaign.cpm_eur)}
                  </div>
                </div>

                {/* Completion Percentage */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Completion</div>
                  <div className="text-2xl font-semibold text-gray-900" data-testid="completion-percentage">
                    {drillDownData.campaign.performance_metrics
                      ? `${(drillDownData.campaign.performance_metrics.projected_completion * 100).toFixed(0)}%`
                      : 'N/A'
                    }
                  </div>
                </div>

                {/* Days Remaining */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Days Remaining</div>
                  <div className="text-2xl font-semibold text-gray-900" data-testid="days-remaining">
                    {drillDownData.campaign.performance_metrics
                      ? `${drillDownData.campaign.performance_metrics.days_remaining} days`
                      : 'N/A'
                    }
                  </div>
                </div>

                {/* Fulfillment Status */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-gray-600">Fulfillment Status</div>
                  <div className="mt-2">
                    {drillDownData.fulfillment_analysis && (
                      <span className={getFulfillmentStatusClasses(drillDownData.fulfillment_analysis.status)}>
                        {drillDownData.fulfillment_analysis.fulfillment_percentage.toFixed(1)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Campaign Timeline */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Campaign Timeline</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4" data-testid="campaign-timeline">
                  <div>
                    <div className="text-sm font-medium text-gray-600">Start Date</div>
                    <div className="text-sm text-gray-900" data-testid="campaign-start">
                      {drillDownData.campaign.runtime_start ?
                        new Date(drillDownData.campaign.runtime_start).toLocaleDateString() :
                        'ASAP'
                      }
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-600">End Date</div>
                    <div className="text-sm text-gray-900" data-testid="campaign-end">
                      {new Date(drillDownData.campaign.runtime_end).toLocaleDateString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-600">Duration</div>
                    <div className="text-sm text-gray-900">
                      {drillDownData.campaign.performance_metrics?.days_remaining || 0} days remaining
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                {drillDownData.campaign.performance_metrics && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                      <span>Progress</span>
                      <span>{(drillDownData.campaign.performance_metrics.projected_completion * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.min(100, drillDownData.campaign.performance_metrics.projected_completion * 100)}%`
                        }}
                        data-testid="timeline-progress-bar"
                        aria-valuenow={drillDownData.campaign.performance_metrics.projected_completion * 100}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Performance Analysis */}
              {drillDownData.fulfillment_analysis && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Analysis</h3>
                  <div className="space-y-3">
                    <div>
                      <span className="text-sm font-medium text-gray-600">Recommendation: </span>
                      <span className="text-sm text-gray-900">{drillDownData.fulfillment_analysis.recommendation}</span>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-600">Variance from Goal: </span>
                      <span className={`text-sm font-medium ${
                        drillDownData.fulfillment_analysis.variance_from_goal >= 0
                          ? 'text-fulfillment-excellent'
                          : 'text-fulfillment-critical'
                      }`}>
                        {drillDownData.fulfillment_analysis.variance_from_goal >= 0 ? '+' : ''}
                        {apiUtils.formatNumber(drillDownData.fulfillment_analysis.variance_from_goal)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <footer className="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                <div className="flex flex-wrap gap-2">
                  {!isEditing && (
                    <button
                      onClick={() => setIsEditing(true)}
                      className="btn btn-secondary text-sm"
                      aria-label="Edit campaign"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Edit Campaign
                    </button>
                  )}

                  <button
                    onClick={handlePauseCampaign}
                    className="btn btn-secondary text-sm"
                    aria-label="Pause campaign"
                  >
                    <Pause className="w-4 h-4 mr-2" />
                    Pause Campaign
                  </button>

                  <button
                    onClick={handleDuplicateCampaign}
                    className="btn btn-secondary text-sm"
                    aria-label="Duplicate campaign"
                  >
                    <Copy className="w-4 h-4 mr-2" />
                    Duplicate Campaign
                  </button>

                  <button
                    onClick={handleExportData}
                    className="btn btn-secondary text-sm"
                    aria-label="Export data"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export Data
                  </button>

                  <button
                    onClick={handleViewFullReport}
                    className="btn btn-secondary text-sm"
                    aria-label="View full report"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    View Full Report
                  </button>
                </div>

                <button
                  onClick={handleClose}
                  className="btn btn-primary text-sm"
                  aria-label="Close modal"
                >
                  Close
                </button>
              </div>
            </footer>
          </>
        )}
      </div>
    </div>,
    document.body
  )
}

export default CampaignDetailModal