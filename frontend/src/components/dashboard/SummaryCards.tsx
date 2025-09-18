/**
 * Summary Cards Component
 *
 * KPI overview cards for system health and fulfillment analysis.
 * Displays key metrics with visual indicators for quick assessment.
 */

import React from 'react'
import { TrendingUp, TrendingDown, AlertTriangle, Target } from 'lucide-react'
import { AnalyticsSummary, SystemHealthMetrics, BaseComponentProps } from '@/types'
import { apiUtils } from '@/lib/api'

interface SummaryCardsProps extends BaseComponentProps {
  analyticsSummary: AnalyticsSummary | null
  systemHealthMetrics: SystemHealthMetrics
  campaignsRequiringAttention: number
}

interface SummaryCardProps {
  title: string
  value: string | number
  subtitle?: string
  trend?: 'up' | 'down' | 'neutral'
  status?: 'success' | 'warning' | 'error' | 'info'
  icon?: React.ReactNode
  'data-testid'?: string
}

const SummaryCard: React.FC<SummaryCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  status = 'info',
  icon,
  'data-testid': testId
}) => {
  const statusClasses = {
    success: 'border-fulfillment-excellent/20 bg-fulfillment-excellent/5',
    warning: 'border-fulfillment-warning/20 bg-fulfillment-warning/5',
    error: 'border-fulfillment-critical/20 bg-fulfillment-critical/5',
    info: 'border-gray-200 bg-white'
  }

  const valueClasses = {
    success: 'text-fulfillment-excellent',
    warning: 'text-fulfillment-warning',
    error: 'text-fulfillment-critical',
    info: 'text-gray-900'
  }

  return (
    <div
      className={`p-6 rounded-lg border ${statusClasses[status]} transition-colors`}
      data-testid={testId}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className="flex items-baseline mt-2">
            <p className={`text-2xl font-semibold ${valueClasses[status]}`}>
              {value}
            </p>
            {trend && (
              <span className={`ml-2 flex items-center text-sm ${
                trend === 'up'
                  ? 'text-fulfillment-excellent'
                  : trend === 'down'
                  ? 'text-fulfillment-critical'
                  : 'text-gray-500'
              }`}>
                {trend === 'up' && <TrendingUp className="w-4 h-4" />}
                {trend === 'down' && <TrendingDown className="w-4 h-4" />}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`p-2 rounded-lg ${
            status === 'success' ? 'bg-fulfillment-excellent/10' :
            status === 'warning' ? 'bg-fulfillment-warning/10' :
            status === 'error' ? 'bg-fulfillment-critical/10' :
            'bg-gray-100'
          }`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}

const SummaryCards: React.FC<SummaryCardsProps> = ({
  analyticsSummary,
  systemHealthMetrics,
  campaignsRequiringAttention,
  className = '',
  'data-testid': testId = 'summary-cards'
}) => {
  if (!analyticsSummary) {
    return (
      <div className={`dashboard-summary-cards ${className}`} data-testid={testId}>
        {/* Loading skeleton */}
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card">
            <div className="loading-skeleton h-4 w-24 mb-2"></div>
            <div className="loading-skeleton h-8 w-16"></div>
          </div>
        ))}
      </div>
    )
  }

  // Calculate derived metrics
  const totalCampaigns = analyticsSummary.total_campaigns + analyticsSummary.total_deals
  const overallFulfillmentRate = analyticsSummary.overall_fulfillment_rate
  const budgetUtilization = analyticsSummary.total_budget_eur > 0
    ? (analyticsSummary.budget_spent_eur / analyticsSummary.total_budget_eur) * 100
    : 0

  // Determine system health status
  const systemHealthStatus = systemHealthMetrics.overall_system_health === 'healthy'
    ? 'success'
    : systemHealthMetrics.overall_system_health === 'degraded'
    ? 'warning'
    : 'error'

  return (
    <div className={`dashboard-summary-cards ${className}`} data-testid={testId}>
      {/* Total Campaigns */}
      <SummaryCard
        title="Total Campaigns"
        value={totalCampaigns.toLocaleString()}
        subtitle={`${analyticsSummary.total_campaigns} campaigns, ${analyticsSummary.total_deals} deals`}
        status="info"
        icon={<Target className="w-5 h-5 text-gray-600" />}
        data-testid="total-campaigns-card"
      />

      {/* Overall Fulfillment Rate */}
      <SummaryCard
        title="Overall Fulfillment"
        value={`${overallFulfillmentRate.toFixed(1)}%`}
        subtitle={`${apiUtils.formatNumber(analyticsSummary.total_impressions_delivered)} / ${apiUtils.formatNumber(analyticsSummary.total_impression_goal)} impressions`}
        status={
          overallFulfillmentRate >= 100 ? 'success' :
          overallFulfillmentRate >= 95 ? 'warning' : 'error'
        }
        trend={
          overallFulfillmentRate >= 100 ? 'up' :
          overallFulfillmentRate < 90 ? 'down' : 'neutral'
        }
        icon={<TrendingUp className="w-5 h-5" />}
        data-testid="fulfillment-rate-card"
      />

      {/* Budget Utilization */}
      <SummaryCard
        title="Budget Utilization"
        value={`${budgetUtilization.toFixed(1)}%`}
        subtitle={`${apiUtils.formatCurrency(analyticsSummary.budget_spent_eur)} / ${apiUtils.formatCurrency(analyticsSummary.total_budget_eur)}`}
        status={
          budgetUtilization >= 90 ? 'success' :
          budgetUtilization >= 70 ? 'warning' : 'error'
        }
        icon={<Target className="w-5 h-5" />}
        data-testid="budget-utilization-card"
      />

      {/* Campaigns Requiring Attention */}
      <SummaryCard
        title="Need Attention"
        value={campaignsRequiringAttention}
        subtitle={
          campaignsRequiringAttention === 0
            ? 'All campaigns performing well'
            : `${campaignsRequiringAttention} campaigns underperforming`
        }
        status={
          campaignsRequiringAttention === 0 ? 'success' :
          campaignsRequiringAttention <= 3 ? 'warning' : 'error'
        }
        icon={
          campaignsRequiringAttention > 0 ? (
            <AlertTriangle className="w-5 h-5" />
          ) : (
            <Target className="w-5 h-5" />
          )
        }
        data-testid="attention-required-card"
      />

      {/* System Health Score */}
      <SummaryCard
        title="System Health"
        value={`${systemHealthMetrics.system_health_score.toFixed(0)}/100`}
        subtitle={
          systemHealthMetrics.overall_system_health === 'healthy'
            ? 'System operating optimally'
            : systemHealthMetrics.overall_system_health === 'degraded'
            ? 'Performance degradation detected'
            : 'Critical system issues'
        }
        status={systemHealthStatus}
        trend={
          systemHealthMetrics.trend_indicators.performance_momentum > 0.1 ? 'up' :
          systemHealthMetrics.trend_indicators.performance_momentum < -0.1 ? 'down' : 'neutral'
        }
        icon={
          systemHealthStatus === 'success' ? (
            <TrendingUp className="w-5 h-5 text-fulfillment-excellent" />
          ) : systemHealthStatus === 'warning' ? (
            <AlertTriangle className="w-5 h-5 text-fulfillment-warning" />
          ) : (
            <TrendingDown className="w-5 h-5 text-fulfillment-critical" />
          )
        }
        data-testid="system-health-card"
      />

      {/* Capacity Utilization */}
      <SummaryCard
        title="Capacity Utilization"
        value={`${systemHealthMetrics.capacity_utilization.toFixed(1)}%`}
        subtitle={
          systemHealthMetrics.capacity_utilization > 95
            ? 'Near capacity limits'
            : systemHealthMetrics.capacity_utilization > 80
            ? 'Good utilization'
            : 'Under-utilized capacity'
        }
        status={
          systemHealthMetrics.capacity_utilization > 95 ? 'warning' :
          systemHealthMetrics.capacity_utilization > 70 ? 'success' : 'info'
        }
        icon={<Target className="w-5 h-5" />}
        data-testid="capacity-utilization-card"
      />

      {/* Performance Distribution */}
      <SummaryCard
        title="Performance Distribution"
        value={`${analyticsSummary.fulfillment_distribution.excellent + analyticsSummary.fulfillment_distribution.good}`}
        subtitle={`${analyticsSummary.fulfillment_distribution.excellent} excellent, ${analyticsSummary.fulfillment_distribution.good} good performers`}
        status={
          (analyticsSummary.fulfillment_distribution.excellent + analyticsSummary.fulfillment_distribution.good) / totalCampaigns > 0.8
            ? 'success' : 'warning'
        }
        icon={<TrendingUp className="w-5 h-5" />}
        data-testid="performance-distribution-card"
      />

      {/* Average Fulfillment Trend */}
      <SummaryCard
        title="Fulfillment Trend"
        value={systemHealthMetrics.trend_indicators.fulfillment_trend}
        subtitle={`Average rate: ${systemHealthMetrics.average_fulfillment_rate.toFixed(1)}%`}
        status={
          systemHealthMetrics.trend_indicators.fulfillment_trend === 'improving' ? 'success' :
          systemHealthMetrics.trend_indicators.fulfillment_trend === 'declining' ? 'error' : 'info'
        }
        trend={
          systemHealthMetrics.trend_indicators.fulfillment_trend === 'improving' ? 'up' :
          systemHealthMetrics.trend_indicators.fulfillment_trend === 'declining' ? 'down' : 'neutral'
        }
        icon={
          systemHealthMetrics.trend_indicators.fulfillment_trend === 'improving' ? (
            <TrendingUp className="w-5 h-5" />
          ) : systemHealthMetrics.trend_indicators.fulfillment_trend === 'declining' ? (
            <TrendingDown className="w-5 h-5" />
          ) : (
            <Target className="w-5 h-5" />
          )
        }
        data-testid="fulfillment-trend-card"
      />
    </div>
  )
}

export default SummaryCards