/**
 * Fulfillment Analysis Utilities
 *
 * Core business logic for campaign fulfillment analysis and system health insights.
 * Focus on impression delivery analysis for PM investigation workflows.
 */

import {
  Campaign,
  FulfillmentStatus,
  SystemHealthMetrics,
  FULFILLMENT_THRESHOLDS,
  FULFILLMENT_COLORS,
} from '@/types'

/**
 * Calculate fulfillment percentage from campaign data
 */
export function calculateFulfillmentPercentage(
  deliveredImpressions: number,
  impressionGoal: number
): number {
  if (impressionGoal === 0) return 0
  return (deliveredImpressions / impressionGoal) * 100
}

/**
 * Determine fulfillment status based on percentage
 * Critical for color coding and system health analysis
 */
export function getFulfillmentStatus(percentage: number): FulfillmentStatus {
  if (percentage >= FULFILLMENT_THRESHOLDS.EXCELLENT) return 'excellent'
  if (percentage >= FULFILLMENT_THRESHOLDS.GOOD) return 'good'
  if (percentage >= FULFILLMENT_THRESHOLDS.WARNING) return 'warning'
  return 'critical'
}

/**
 * Get CSS classes for fulfillment status display
 */
export function getFulfillmentStatusClasses(status: FulfillmentStatus): string {
  return `fulfillment-status ${FULFILLMENT_COLORS[status]}`
}

/**
 * Get human-readable status label
 */
export function getFulfillmentStatusLabel(percentage: number): string {
  const status = getFulfillmentStatus(percentage)

  switch (status) {
    case 'excellent':
      return percentage >= 100 ? 'Goal Exceeded' : 'Goal Met'
    case 'good':
      return 'Near Goal'
    case 'warning':
      return 'Moderate Shortfall'
    case 'critical':
      return 'Critical Shortfall'
    default:
      return 'Unknown'
  }
}

/**
 * Calculate variance from goal for detailed analysis
 */
export function calculateVarianceFromGoal(
  deliveredImpressions: number,
  impressionGoal: number
): number {
  return deliveredImpressions - impressionGoal
}

/**
 * Analyze campaign performance and provide recommendations
 */
export function analyzeCampaignPerformance(campaign: Campaign): {
  status: FulfillmentStatus
  recommendation: string
  urgency: 'low' | 'medium' | 'high'
  actionRequired: boolean
} {
  const deliveredImpressions = campaign.delivered_impressions || 0
  const fulfillmentPercentage = calculateFulfillmentPercentage(
    deliveredImpressions,
    campaign.impression_goal
  )
  const status = getFulfillmentStatus(fulfillmentPercentage)

  let recommendation = ''
  let urgency: 'low' | 'medium' | 'high' = 'low'
  let actionRequired = false

  switch (status) {
    case 'excellent':
      recommendation = fulfillmentPercentage > 110
        ? 'Consider reallocating excess capacity to underperforming campaigns'
        : 'Performance optimal. Monitor for continued success'
      urgency = 'low'
      actionRequired = false
      break

    case 'good':
      recommendation = 'On track for goal achievement. Monitor delivery rate'
      urgency = 'low'
      actionRequired = false
      break

    case 'warning':
      recommendation = 'Review targeting and bid strategy. Increase delivery rate'
      urgency = 'medium'
      actionRequired = true
      break

    case 'critical':
      recommendation = 'Immediate action required. Check system capacity and targeting'
      urgency = 'high'
      actionRequired = true
      break
  }

  return { status, recommendation, urgency, actionRequired }
}

/**
 * Calculate system health metrics for dashboard overview
 */
export function calculateSystemHealthMetrics(campaigns: Campaign[]): SystemHealthMetrics {
  if (campaigns.length === 0) {
    return {
      overall_system_health: 'healthy',
      capacity_utilization: 0,
      average_fulfillment_rate: 0,
      campaigns_requiring_attention: 0,
      projected_completion_accuracy: 0,
      trend_indicators: {
        fulfillment_trend: 'stable',
        capacity_trend: 'stable',
        performance_momentum: 0,
      },
    }
  }

  // Calculate fulfillment rates for all campaigns
  const fulfillmentRates = campaigns
    .filter(c => c.delivered_impressions !== undefined)
    .map(c => calculateFulfillmentPercentage(
      c.delivered_impressions || 0,
      c.impression_goal
    ))

  const averageFulfillmentRate = fulfillmentRates.length > 0
    ? fulfillmentRates.reduce((sum, rate) => sum + rate, 0) / fulfillmentRates.length
    : 0

  // Count campaigns by status
  const statusCounts = campaigns.reduce((acc, campaign) => {
    const deliveredImpressions = campaign.delivered_impressions || 0
    const fulfillmentPercentage = calculateFulfillmentPercentage(
      deliveredImpressions,
      campaign.impression_goal
    )
    const status = getFulfillmentStatus(fulfillmentPercentage)
    acc[status] = (acc[status] || 0) + 1
    return acc
  }, {} as Record<FulfillmentStatus, number>)

  // Determine overall system health
  const criticalCount = statusCounts.critical || 0
  const warningCount = statusCounts.warning || 0
  const totalCampaigns = campaigns.length

  let overall_system_health: 'healthy' | 'degraded' | 'critical'
  if (criticalCount / totalCampaigns > 0.2) {
    overall_system_health = 'critical'
  } else if ((criticalCount + warningCount) / totalCampaigns > 0.3) {
    overall_system_health = 'degraded'
  } else {
    overall_system_health = 'healthy'
  }

  // Calculate capacity utilization
  const totalImpressionGoal = campaigns.reduce((sum, c) => sum + c.impression_goal, 0)
  const totalDeliveredImpressions = campaigns.reduce(
    (sum, c) => sum + (c.delivered_impressions || 0),
    0
  )
  const capacityUtilization = totalImpressionGoal > 0
    ? (totalDeliveredImpressions / totalImpressionGoal) * 100
    : 0

  // Calculate campaigns requiring attention
  const campaignsRequiringAttention = criticalCount + warningCount

  return {
    overall_system_health,
    capacity_utilization: Math.min(100, capacityUtilization),
    average_fulfillment_rate: averageFulfillmentRate,
    campaigns_requiring_attention: campaignsRequiringAttention,
    projected_completion_accuracy: calculateProjectionAccuracy(campaigns),
    trend_indicators: {
      fulfillment_trend: calculateFulfillmentTrend(campaigns),
      capacity_trend: 'stable', // Would need historical data
      performance_momentum: calculatePerformanceMomentum(fulfillmentRates),
    },
  }
}

/**
 * Calculate projection accuracy for system health assessment
 */
function calculateProjectionAccuracy(campaigns: Campaign[]): number {
  // Simplified calculation - in real implementation would compare
  // projected vs actual completion rates
  const completedCampaigns = campaigns.filter(c => !c.is_running)
  if (completedCampaigns.length === 0) return 85 // Default for active campaigns

  const accurateProjections = completedCampaigns.filter(c => {
    const deliveredImpressions = c.delivered_impressions || 0
    const fulfillmentPercentage = calculateFulfillmentPercentage(
      deliveredImpressions,
      c.impression_goal
    )
    // Consider projection accurate if within 5% of goal
    return Math.abs(fulfillmentPercentage - 100) <= 5
  }).length

  return (accurateProjections / completedCampaigns.length) * 100
}

/**
 * Calculate fulfillment trend indicator
 */
function calculateFulfillmentTrend(campaigns: Campaign[]): 'improving' | 'stable' | 'declining' {
  // Simplified - would need historical data for real trend analysis
  const activeCampaigns = campaigns.filter(c => c.is_running)
  const averageFulfillment = activeCampaigns.reduce((sum, c) => {
    const deliveredImpressions = c.delivered_impressions || 0
    return sum + calculateFulfillmentPercentage(deliveredImpressions, c.impression_goal)
  }, 0) / activeCampaigns.length

  if (averageFulfillment > 95) return 'improving'
  if (averageFulfillment < 85) return 'declining'
  return 'stable'
}

/**
 * Calculate performance momentum (-1 to 1 scale)
 */
function calculatePerformanceMomentum(fulfillmentRates: number[]): number {
  if (fulfillmentRates.length === 0) return 0

  const average = fulfillmentRates.reduce((sum, rate) => sum + rate, 0) / fulfillmentRates.length

  // Normalize to -1 to 1 scale based on how far above/below optimal performance
  const normalizedMomentum = (average - 100) / 100
  return Math.max(-1, Math.min(1, normalizedMomentum))
}

/**
 * Filter campaigns by fulfillment status for investigation workflows
 */
export function filterCampaignsByFulfillmentStatus(
  campaigns: Campaign[],
  status: FulfillmentStatus
): Campaign[] {
  return campaigns.filter(campaign => {
    const deliveredImpressions = campaign.delivered_impressions || 0
    const fulfillmentPercentage = calculateFulfillmentPercentage(
      deliveredImpressions,
      campaign.impression_goal
    )
    return getFulfillmentStatus(fulfillmentPercentage) === status
  })
}

/**
 * Get campaigns requiring immediate attention
 */
export function getCampaignsRequiringAttention(campaigns: Campaign[]): Campaign[] {
  return campaigns.filter(campaign => {
    const analysis = analyzeCampaignPerformance(campaign)
    return analysis.actionRequired
  })
}

/**
 * Calculate expected completion date based on current delivery rate
 */
export function calculateExpectedCompletion(
  campaign: Campaign,
  currentDeliveryRate: number
): Date | null {
  if (!campaign.is_running || currentDeliveryRate <= 0) return null

  const deliveredImpressions = campaign.delivered_impressions || 0
  const remainingImpressions = campaign.impression_goal - deliveredImpressions

  if (remainingImpressions <= 0) return new Date() // Already completed

  const daysToCompletion = remainingImpressions / currentDeliveryRate
  const completionDate = new Date()
  completionDate.setDate(completionDate.getDate() + daysToCompletion)

  return completionDate
}