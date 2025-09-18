/**
 * Charts Section Component
 *
 * Analytics visualization section for fulfillment analysis.
 * Uses Recharts for campaign vs deal distribution and performance trends.
 */

import React, { useMemo } from 'react'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'
import { Campaign, AnalyticsSummary, BaseComponentProps } from '@/types'
import { getFulfillmentStatus, calculateFulfillmentPercentage } from '@/lib/fulfillment'
import { apiUtils } from '@/lib/api'

interface ChartsSectionProps extends BaseComponentProps {
  campaigns: Campaign[]
  analyticsSummary: AnalyticsSummary | null
  onDrillDown: (campaign: Campaign) => void
}

const ChartsSection: React.FC<ChartsSectionProps> = ({
  campaigns,
  analyticsSummary,
  onDrillDown,
  className = '',
  'data-testid': testId = 'charts-section'
}) => {
  /**
   * Prepare campaign vs deal distribution data
   */
  const distributionData = useMemo(() => {
    if (!analyticsSummary) return []

    return [
      {
        name: 'Campaigns',
        value: analyticsSummary.total_campaigns,
        budget: analyticsSummary.budget_distribution?.campaigns || 0,
        color: '#3b82f6'
      },
      {
        name: 'Deals',
        value: analyticsSummary.total_deals,
        budget: analyticsSummary.budget_distribution?.deals || 0,
        color: '#8b5cf6'
      }
    ]
  }, [analyticsSummary])

  /**
   * Prepare fulfillment performance data
   */
  const fulfillmentData = useMemo(() => {
    if (!analyticsSummary) return []

    const distribution = analyticsSummary.fulfillment_distribution
    return [
      {
        name: 'Excellent (≥100%)',
        count: distribution.excellent,
        color: '#22c55e',
        threshold: '≥100%'
      },
      {
        name: 'Good (98-99.9%)',
        count: distribution.good,
        color: '#eab308',
        threshold: '98-99.9%'
      },
      {
        name: 'Warning (95-98%)',
        count: distribution.warning,
        color: '#f97316',
        threshold: '95-98%'
      },
      {
        name: 'Critical (<95%)',
        count: distribution.critical,
        color: '#ef4444',
        threshold: '<95%'
      }
    ]
  }, [analyticsSummary])

  /**
   * Custom tooltip for pie charts
   */
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{data.name}</p>
          <p className="text-sm text-gray-600">
            Count: {data.value || data.count}
          </p>
          {data.budget && (
            <p className="text-sm text-gray-600">
              Budget: {apiUtils.formatCurrency(data.budget)}
            </p>
          )}
          {data.threshold && (
            <p className="text-sm text-gray-600">
              Range: {data.threshold}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  /**
   * Top performing campaigns for drill-down
   */
  const topPerformingCampaigns = useMemo(() => {
    return campaigns
      .filter(c => c.delivered_impressions !== undefined)
      .map(c => ({
        ...c,
        fulfillmentPercentage: calculateFulfillmentPercentage(
          c.delivered_impressions || 0,
          c.impression_goal
        )
      }))
      .sort((a, b) => b.fulfillmentPercentage - a.fulfillmentPercentage)
      .slice(0, 5)
  }, [campaigns])

  if (!analyticsSummary) {
    return (
      <div className={`space-y-6 ${className}`} data-testid={testId}>
        {/* Loading skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <div className="loading-skeleton h-64"></div>
          </div>
          <div className="card">
            <div className="loading-skeleton h-64"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`} data-testid={testId}>
      {/* Chart Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Campaign vs Deal Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Campaign vs Deal Distribution</h3>
            <p className="card-subtitle">Count and budget allocation</p>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart data-testid="campaign-distribution-chart">
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) =>
                    `${name}: ${value} (${(percent * 100).toFixed(1)}%)`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fulfillment Performance Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Fulfillment Performance</h3>
            <p className="card-subtitle">Campaign count by performance level</p>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={fulfillmentData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                data-testid="fulfillment-performance-chart"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#8884d8">
                  {fulfillmentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Performing Campaigns */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Top Performing Campaigns</h3>
          <p className="card-subtitle">Highest fulfillment rates - click to drill down</p>
        </div>

        <div className="space-y-3">
          {topPerformingCampaigns.map((campaign, index) => {
            const fulfillmentStatus = getFulfillmentStatus(campaign.fulfillmentPercentage)

            return (
              <div
                key={campaign.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                onClick={() => onDrillDown(campaign)}
                data-testid={`top-campaign-${index}`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-gray-500">
                      #{index + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {campaign.name}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">
                          {apiUtils.formatNumber(campaign.delivered_impressions || 0)} / {apiUtils.formatNumber(campaign.impression_goal)}
                        </span>
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            campaign.campaign_type === 'campaign'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-purple-100 text-purple-800'
                          }`}
                        >
                          {campaign.campaign_type}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <div className={`text-sm font-semibold ${
                      fulfillmentStatus === 'excellent' ? 'text-fulfillment-excellent' :
                      fulfillmentStatus === 'good' ? 'text-fulfillment-good' :
                      fulfillmentStatus === 'warning' ? 'text-fulfillment-warning' :
                      'text-fulfillment-critical'
                    }`}>
                      {campaign.fulfillmentPercentage.toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {apiUtils.formatCurrency(campaign.budget_eur)}
                    </div>
                  </div>
                  <div className={`w-3 h-3 rounded-full ${
                    fulfillmentStatus === 'excellent' ? 'bg-fulfillment-excellent' :
                    fulfillmentStatus === 'good' ? 'bg-fulfillment-good' :
                    fulfillmentStatus === 'warning' ? 'bg-fulfillment-warning' :
                    'bg-fulfillment-critical'
                  }`} />
                </div>
              </div>
            )
          })}
        </div>

        {topPerformingCampaigns.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>No campaign performance data available</p>
          </div>
        )}
      </div>

      {/* System Health Summary */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">System Health Summary</h3>
          <p className="card-subtitle">Key metrics overview</p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-semibold text-gray-900">
              {analyticsSummary.overall_fulfillment_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Overall Fulfillment</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-semibold text-gray-900">
              {apiUtils.formatNumber(analyticsSummary.total_impression_goal)}
            </div>
            <div className="text-sm text-gray-600">Total Goal</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-semibold text-gray-900">
              {apiUtils.formatCurrency(analyticsSummary.total_budget_eur)}
            </div>
            <div className="text-sm text-gray-600">Total Budget</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-semibold text-gray-900">
              {analyticsSummary.total_campaigns + analyticsSummary.total_deals}
            </div>
            <div className="text-sm text-gray-600">Total Items</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChartsSection