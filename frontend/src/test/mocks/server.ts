/**
 * Mock Service Worker Server Configuration
 *
 * Discovery-Driven API Mocking:
 * - Simulates backend API responses for frontend testing
 * - Supports discovery testing with flexible response scenarios
 * - Enables testing without backend dependency
 * - Facilitates rapid UI iteration and experimentation
 */

import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

// Mock API responses for campaign data
const campaignHandlers = [
  // GET /api/v1/campaigns - List all campaigns with filtering
  http.get('*/api/v1/campaigns', ({ request }) => {
    const url = new URL(request.url)
    const type = url.searchParams.get('type')
    const running = url.searchParams.get('running')
    const search = url.searchParams.get('search')

    let campaigns = [...mockCampaignData]

    // Apply filters
    if (type) {
      campaigns = campaigns.filter(c => c.campaign_type === type)
    }
    if (running !== null) {
      const isRunning = running === 'true'
      campaigns = campaigns.filter(c => c.is_running === isRunning)
    }
    if (search) {
      campaigns = campaigns.filter(c =>
        c.name.toLowerCase().includes(search.toLowerCase())
      )
    }

    return HttpResponse.json({ data: campaigns })
  }),

  // GET /api/v1/campaigns/{id} - Get specific campaign
  rest.get('*/api/v1/campaigns/:id', (req, res, ctx) => {
    const { id } = req.params
    const campaign = mockCampaignData.find(c => c.id === id)

    if (!campaign) {
      return res(
        ctx.status(404),
        ctx.json({
          error: 'Campaign not found',
          message: `Campaign with ID ${id} does not exist`
        })
      )
    }

    return res(
      ctx.status(200),
      ctx.json(campaign)
    )
  }),

  // POST /api/v1/campaigns/upload - Upload XLSX file
  rest.post('*/api/v1/campaigns/upload', (req, res, ctx) => {
    // Simulate successful upload
    return res(
      ctx.status(201),
      ctx.json({
        processed_count: 25,
        failed_count: 0,
        campaign_ids: mockCampaignData.slice(0, 25).map(c => c.id),
        message: 'Campaigns uploaded successfully'
      })
    )
  }),

  // GET /api/v1/campaigns/analytics/summary - Analytics summary
  rest.get('*/api/v1/campaigns/analytics/summary', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockAnalyticsSummary)
    )
  }),

  // GET /api/v1/campaigns/analytics/budget-distribution - Budget analytics
  rest.get('*/api/v1/campaigns/analytics/budget-distribution', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockBudgetDistribution)
    )
  }),

  // GET /api/v1/campaigns/analytics/performance - Performance metrics
  rest.get('*/api/v1/campaigns/analytics/performance', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(mockPerformanceMetrics)
    )
  })
]

// Error simulation handlers for discovery testing
const errorHandlers = [
  // Simulate network error
  rest.get('*/api/v1/campaigns/error/network', (req, res, ctx) => {
    return res.networkError('Network connection failed')
  }),

  // Simulate server error
  rest.get('*/api/v1/campaigns/error/server', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({
        error: 'Internal Server Error',
        message: 'Something went wrong on the server'
      })
    )
  }),

  // Simulate timeout
  rest.get('*/api/v1/campaigns/error/timeout', (req, res, ctx) => {
    return res(
      ctx.delay(10000), // 10 second delay to simulate timeout
      ctx.status(200),
      ctx.json([])
    )
  })
]

// Mock data that matches backend fixtures
const mockCampaignData = [
  {
    id: '56cc787c-a703-4cd3-995a-4b42eb408dfb',
    name: '2025_10147_0303_1_PV Promotion | UML | GIGA | CN-Autorinnen-Ausschreibung 2025',
    campaign_type: 'campaign',
    is_running: true,
    runtime_start: null,
    runtime_end: '2025-06-30',
    impression_goal: 2000000000,
    budget_eur: 2396690.38,
    cpm_eur: 1.183,
    buyer: 'Not set',
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    name: 'Summer Campaign 2025 | Fashion | Premium Inventory',
    campaign_type: 'deal',
    is_running: true,
    runtime_start: '2025-07-07',
    runtime_end: '2025-07-24',
    impression_goal: 1500000,
    budget_eur: 125000.50,
    cpm_eur: 2.45,
    buyer: 'DENTSU_AEGIS < Easymedia_rtb (Seat 608194)',
    created_at: '2025-01-02T00:00:00Z'
  },
  {
    id: 'b2c3d4e5-f6g7-8901-bcde-f23456789012',
    name: 'Completed Q1 Campaign 2024 | Tech | Mobile',
    campaign_type: 'campaign',
    is_running: false,
    runtime_start: '2024-02-15',
    runtime_end: '2024-02-28',
    impression_goal: 750000,
    budget_eur: 45000.00,
    cmp_eur: 0.95,
    buyer: 'Not set',
    created_at: '2024-02-01T00:00:00Z'
  },
  {
    id: 'c3d4e5f6-g7h8-9012-cdef-345678901234',
    name: 'Year-end ASAP Campaign | Retail | Desktop+Mobile',
    campaign_type: 'deal',
    is_running: true,
    runtime_start: null,
    runtime_end: '2025-12-31',
    impression_goal: 5000000,
    budget_eur: 1500000.75,
    cpm_eur: 3.25,
    buyer: 'AMAZON_DSP < Amazon_DSP (Seat 789012)',
    created_at: '2025-01-03T00:00:00Z'
  }
]

const mockAnalyticsSummary = {
  total_campaigns: 150,
  total_deals: 75,
  running_campaigns: 45,
  completed_campaigns: 180,
  total_budget_eur: 5500000.00,
  average_cpm_eur: 2.15,
  last_updated: '2025-01-17T10:30:00Z'
}

const mockBudgetDistribution = {
  by_campaign_type: {
    campaigns: 3200000.00,
    deals: 2300000.00
  },
  by_month: [
    { month: 'Jan', budget: 450000, campaigns: 15, deals: 8 },
    { month: 'Feb', budget: 520000, campaigns: 18, deals: 10 },
    { month: 'Mar', budget: 680000, campaigns: 22, deals: 12 },
    { month: 'Apr', budget: 590000, campaigns: 19, deals: 9 },
    { month: 'May', budget: 720000, campaigns: 24, deals: 14 },
    { month: 'Jun', budget: 650000, campaigns: 21, deals: 11 }
  ],
  top_campaigns: [
    {
      id: '56cc787c-a703-4cd3-995a-4b42eb408dfb',
      name: '2025_10147_0303_1_PV Promotion | UML | GIGA | CN-Autorinnen-Ausschreibung 2025',
      budget_eur: 2396690.38,
      campaign_type: 'campaign'
    },
    {
      id: 'c3d4e5f6-g7h8-9012-cdef-345678901234',
      name: 'Year-end ASAP Campaign | Retail | Desktop+Mobile',
      budget_eur: 1500000.75,
      campaign_type: 'deal'
    }
  ]
}

const mockPerformanceMetrics = {
  completion_rate: {
    campaigns: 0.72,
    deals: 0.68,
    overall: 0.70
  },
  budget_utilization: {
    campaigns: 0.85,
    deals: 0.92,
    overall: 0.88
  },
  cpm_trends: [
    { month: 'Jan', avg_cpm: 1.95, campaign_count: 23 },
    { month: 'Feb', avg_cpm: 2.10, campaign_count: 28 },
    { month: 'Mar', avg_cpm: 2.25, campaign_count: 34 },
    { month: 'Apr', avg_cpm: 2.15, campaign_count: 28 },
    { month: 'May', avg_cpm: 2.40, campaign_count: 38 },
    { month: 'Jun', avg_cpm: 2.30, campaign_count: 32 }
  ],
  system_health_score: 0.82,
  recommendations: [
    'Consider optimizing CPM for deal campaigns to improve efficiency',
    'Budget utilization for campaigns can be improved by 15%',
    'Q2 performance shows strong growth trend'
  ]
}

// Create server with all handlers
export const server = setupServer(
  ...campaignHandlers,
  ...errorHandlers
)

// Export mock data for use in tests
export {
  mockCampaignData,
  mockAnalyticsSummary,
  mockBudgetDistribution,
  mockPerformanceMetrics
}

// Helper functions for dynamic mock responses in tests
export const mockServerResponses = {
  /**
   * Mock successful campaign list response
   */
  campaigns: (campaigns = mockCampaignData) => {
    server.use(
      rest.get('*/api/v1/campaigns', (req, res, ctx) => {
        return res(ctx.status(200), ctx.json(campaigns))
      })
    )
  },

  /**
   * Mock campaign upload success
   */
  uploadSuccess: (processedCount = 25, failedCount = 0) => {
    server.use(
      rest.post('*/api/v1/campaigns/upload', (req, res, ctx) => {
        return res(
          ctx.status(201),
          ctx.json({
            processed_count: processedCount,
            failed_count: failedCount,
            campaign_ids: mockCampaignData.slice(0, processedCount).map(c => c.id)
          })
        )
      })
    )
  },

  /**
   * Mock campaign upload failure
   */
  uploadFailure: (errorMessage = 'Invalid file format') => {
    server.use(
      rest.post('*/api/v1/campaigns/upload', (req, res, ctx) => {
        return res(
          ctx.status(400),
          ctx.json({
            error: 'Upload failed',
            message: errorMessage
          })
        )
      })
    )
  },

  /**
   * Mock network error
   */
  networkError: (endpoint = '*/api/v1/campaigns') => {
    server.use(
      rest.get(endpoint, (req, res, ctx) => {
        return res.networkError('Network connection failed')
      })
    )
  },

  /**
   * Mock server error
   */
  serverError: (endpoint = '*/api/v1/campaigns', status = 500) => {
    server.use(
      rest.get(endpoint, (req, res, ctx) => {
        return res(
          ctx.status(status),
          ctx.json({
            error: 'Server Error',
            message: 'An unexpected error occurred'
          })
        )
      })
    )
  },

  /**
   * Mock loading delay for testing loading states
   */
  delayedResponse: (endpoint = '*/api/v1/campaigns', delay = 2000) => {
    server.use(
      rest.get(endpoint, (req, res, ctx) => {
        return res(
          ctx.delay(delay),
          ctx.status(200),
          ctx.json(mockCampaignData)
        )
      })
    )
  }
}

// Mock Service Worker usage examples available in project documentation