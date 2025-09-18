/**
 * Campaign Table Component
 *
 * Data table with fulfillment color coding for system health analysis.
 * Implements TDD specifications for campaign display, selection, and drill-down.
 */

import React, { useState, useMemo } from 'react'
import { ChevronUp, ChevronDown, ExternalLink } from 'lucide-react'
import {
  Campaign,
  BaseComponentProps,
  FulfillmentStatus
} from '@/types'
import {
  calculateFulfillmentPercentage,
  getFulfillmentStatus,
  getFulfillmentStatusClasses,
  getFulfillmentStatusLabel
} from '@/lib/fulfillment'
import { apiUtils } from '@/lib/api'
import LoadingSpinner from '../ui/LoadingSpinner'

interface CampaignTableProps extends BaseComponentProps {
  campaigns: Campaign[]
  selectedCampaigns: string[]
  onSelectionChange: (campaignIds: string[]) => void
  onCampaignClick: (campaign: Campaign) => void
  loading?: boolean
  maxHeight?: string
}

type SortField = 'name' | 'type' | 'fulfillment' | 'budget' | 'goal' | 'status'
type SortDirection = 'asc' | 'desc'

const CampaignTable: React.FC<CampaignTableProps> = ({
  campaigns,
  selectedCampaigns,
  onSelectionChange,
  onCampaignClick,
  loading = false,
  maxHeight = '500px',
  className = '',
  'data-testid': testId = 'campaign-table'
}) => {
  const [sortField, setSortField] = useState<SortField>('fulfillment')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  /**
   * Handle sorting logic
   */
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  /**
   * Sort campaigns based on current sort criteria
   */
  const sortedCampaigns = useMemo(() => {
    return [...campaigns].sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'name':
          aValue = a.name.toLowerCase()
          bValue = b.name.toLowerCase()
          break
        case 'type':
          aValue = a.campaign_type
          bValue = b.campaign_type
          break
        case 'fulfillment':
          aValue = calculateFulfillmentPercentage(
            a.delivered_impressions || 0,
            a.impression_goal
          )
          bValue = calculateFulfillmentPercentage(
            b.delivered_impressions || 0,
            b.impression_goal
          )
          break
        case 'budget':
          aValue = a.budget_eur
          bValue = b.budget_eur
          break
        case 'goal':
          aValue = a.impression_goal
          bValue = b.impression_goal
          break
        case 'status':
          aValue = a.is_running ? 1 : 0
          bValue = b.is_running ? 1 : 0
          break
        default:
          return 0
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1
      return 0
    })
  }, [campaigns, sortField, sortDirection])

  /**
   * Handle individual campaign selection
   */
  const handleCampaignSelection = (campaignId: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedCampaigns, campaignId])
    } else {
      onSelectionChange(selectedCampaigns.filter(id => id !== campaignId))
    }
  }

  /**
   * Handle select all functionality
   */
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectionChange(campaigns.map(c => c.id))
    } else {
      onSelectionChange([])
    }
  }

  /**
   * Calculate fulfillment data for a campaign
   */
  const getCampaignFulfillmentData = (campaign: Campaign) => {
    const deliveredImpressions = campaign.delivered_impressions || 0
    const fulfillmentPercentage = calculateFulfillmentPercentage(
      deliveredImpressions,
      campaign.impression_goal
    )
    const status = getFulfillmentStatus(fulfillmentPercentage)
    const statusLabel = getFulfillmentStatusLabel(fulfillmentPercentage)

    return {
      percentage: fulfillmentPercentage,
      status,
      statusLabel,
      delivered: deliveredImpressions
    }
  }

  /**
   * Render sort icon
   */
  const SortIcon: React.FC<{ field: SortField }> = ({ field }) => {
    if (sortField !== field) return null

    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4 ml-1" />
    ) : (
      <ChevronDown className="w-4 h-4 ml-1" />
    )
  }

  /**
   * Render table header with sorting
   */
  const TableHeader: React.FC<{ field: SortField; children: React.ReactNode }> = ({
    field,
    children
  }) => (
    <th
      className="data-table th cursor-pointer hover:bg-gray-100 select-none"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center">
        {children}
        <SortIcon field={field} />
      </div>
    </th>
  )

  if (loading && campaigns.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner message="Loading campaigns..." />
      </div>
    )
  }

  if (campaigns.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No campaigns found</p>
      </div>
    )
  }

  const isAllSelected = campaigns.length > 0 && selectedCampaigns.length === campaigns.length
  const isPartiallySelected = selectedCampaigns.length > 0 && selectedCampaigns.length < campaigns.length

  return (
    <div className={`${className}`} data-testid={testId}>
      <div className="overflow-auto" style={{ maxHeight }}>
        <table className="data-table">
          <thead>
            <tr>
              <th className="data-table th w-12">
                <input
                  type="checkbox"
                  checked={isAllSelected}
                  ref={(input) => {
                    if (input) input.indeterminate = isPartiallySelected
                  }}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  aria-label="Select all campaigns"
                />
              </th>
              <TableHeader field="name">Campaign Name</TableHeader>
              <TableHeader field="type">Type</TableHeader>
              <TableHeader field="fulfillment">Fulfillment</TableHeader>
              <TableHeader field="goal">Goal</TableHeader>
              <TableHeader field="budget">Budget</TableHeader>
              <TableHeader field="status">Status</TableHeader>
              <th className="data-table th w-12">Action</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedCampaigns.map((campaign) => {
              const fulfillmentData = getCampaignFulfillmentData(campaign)
              const isSelected = selectedCampaigns.includes(campaign.id)

              return (
                <tr
                  key={campaign.id}
                  className={`data-table tbody tr ${isSelected ? 'bg-primary-50' : ''}`}
                  data-testid={`campaign-row-${campaign.id}`}
                >
                  {/* Selection Checkbox */}
                  <td className="data-table td">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={(e) => handleCampaignSelection(campaign.id, e.target.checked)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      aria-label={`Select ${campaign.name}`}
                    />
                  </td>

                  {/* Campaign Name */}
                  <td
                    className="data-table td cursor-pointer hover:text-primary-600"
                    onClick={() => onCampaignClick(campaign)}
                  >
                    <div className="max-w-xs truncate" title={campaign.name}>
                      {campaign.name}
                    </div>
                  </td>

                  {/* Campaign Type */}
                  <td className="data-table td">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        campaign.campaign_type === 'campaign'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-purple-100 text-purple-800'
                      }`}
                      data-testid="campaign-type-badge"
                    >
                      {campaign.campaign_type === 'campaign' ? 'Campaign' : 'Deal'}
                    </span>
                  </td>

                  {/* Fulfillment Percentage */}
                  <td className="data-table td">
                    <div className="flex items-center space-x-2">
                      <span
                        className={getFulfillmentStatusClasses(fulfillmentData.status)}
                        data-testid="fulfillment-status-badge"
                      >
                        {fulfillmentData.percentage.toFixed(1)}%
                      </span>
                      <div className="text-xs text-gray-500">
                        {apiUtils.formatNumber(fulfillmentData.delivered)} / {apiUtils.formatNumber(campaign.impression_goal)}
                      </div>
                    </div>
                  </td>

                  {/* Impression Goal */}
                  <td className="data-table td" data-testid="impression-goal">
                    {apiUtils.formatNumber(campaign.impression_goal)}
                  </td>

                  {/* Budget */}
                  <td className="data-table td" data-testid="budget">
                    {apiUtils.formatCurrency(campaign.budget_eur)}
                  </td>

                  {/* Running Status */}
                  <td className="data-table td">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        campaign.is_running
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                      data-testid="campaign-status"
                    >
                      {campaign.is_running ? 'Running' : 'Completed'}
                    </span>
                  </td>

                  {/* Action Button */}
                  <td className="data-table td">
                    <button
                      onClick={() => onCampaignClick(campaign)}
                      className="text-gray-400 hover:text-primary-600 transition-colors"
                      aria-label={`View details for ${campaign.name}`}
                    >
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Table Footer with Summary */}
      <div className="mt-4 px-2 py-3 bg-gray-50 rounded-b-lg border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            {campaigns.length} campaigns total
            {selectedCampaigns.length > 0 && (
              <span className="ml-2">
                · {selectedCampaigns.length} selected
              </span>
            )}
          </span>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-fulfillment-excellent rounded-full"></div>
              <span>Excellent</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-fulfillment-good rounded-full"></div>
              <span>Good</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-fulfillment-warning rounded-full"></div>
              <span>Warning</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-fulfillment-critical rounded-full"></div>
              <span>Critical</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CampaignTable