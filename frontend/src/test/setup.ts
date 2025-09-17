/**
 * Jest Test Setup for PPV System Health Monitor Frontend
 *
 * Discovery-Driven TDD Test Environment Configuration:
 * - React Testing Library DOM matchers
 * - Mock Service Worker for API testing
 * - Chart testing utilities
 * - Custom test utilities and helpers
 */

import '@testing-library/jest-dom'
import { configure } from '@testing-library/react'
import { server } from './mocks/server'
import { rest } from 'msw'
import 'whatwg-fetch'

// Configure React Testing Library
configure({
  // Increase timeout for async operations in discovery testing
  asyncUtilTimeout: 5000,

  // Custom test ID attribute for better test targeting
  testIdAttribute: 'data-testid',

  // Show suggestions for better queries
  computedStyleSupportsPseudoElements: true
})

// Mock Service Worker setup for API testing
beforeAll(() => {
  // Start the mock server before all tests
  server.listen({
    onUnhandledRequest: 'warn'
  })
})

afterEach(() => {
  // Reset handlers after each test to ensure test isolation
  server.resetHandlers()
})

afterAll(() => {
  // Close the mock server after all tests
  server.close()
})

// Global test utilities and mocks
global.console = {
  ...console,
  // Suppress console.log in tests unless explicitly needed
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
}

// Mock IntersectionObserver for chart visibility testing
global.IntersectionObserver = jest.fn(() => ({
  observe: jest.fn(),
  disconnect: jest.fn(),
  unobserve: jest.fn()
}))

// Mock ResizeObserver for responsive chart testing
global.ResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  disconnect: jest.fn(),
  unobserve: jest.fn()
}))

// Mock matchMedia for responsive design testing
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock window.scrollTo for navigation testing
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: jest.fn()
})

// Custom Jest matchers for discovery-driven testing
expect.extend({
  /**
   * Custom matcher for testing chart data rendering
   * Usage: expect(chartElement).toRenderChartData(expectedData)
   */
  toRenderChartData(received: HTMLElement, expectedData: any[]) {
    const chartElements = received.querySelectorAll('[data-testid*="chart-"]')
    const hasData = chartElements.length > 0
    const dataPoints = Array.from(chartElements).length

    if (hasData && dataPoints === expectedData.length) {
      return {
        message: () => `Chart renders expected ${expectedData.length} data points`,
        pass: true
      }
    }

    return {
      message: () => `Expected chart to render ${expectedData.length} data points, but found ${dataPoints}`,
      pass: false
    }
  },

  /**
   * Custom matcher for testing responsive behavior
   * Usage: expect(component).toBeResponsive()
   */
  toBeResponsive(received: HTMLElement) {
    const hasResponsiveClasses = received.className.includes('responsive') ||
                                received.className.includes('sm:') ||
                                received.className.includes('md:') ||
                                received.className.includes('lg:')

    if (hasResponsiveClasses) {
      return {
        message: () => `Element has responsive classes`,
        pass: true
      }
    }

    return {
      message: () => `Expected element to have responsive classes (responsive, sm:, md:, lg:)`,
      pass: false
    }
  }
})

// Global test data for discovery scenarios
global.testData = {
  // Sample campaign data matching backend fixtures
  sampleCampaigns: [
    {
      id: '56cc787c-a703-4cd3-995a-4b42eb408dfb',
      name: '2025_10147_0303_1_PV Promotion | UML | GIGA | CN-Autorinnen-Ausschreibung 2025',
      campaign_type: 'campaign',
      is_running: true,
      budget_eur: 2396690.38,
      cpm_eur: 1.183,
      runtime_end: '2025-06-30',
      buyer: 'Not set'
    },
    {
      id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
      name: 'Summer Campaign 2025 | Fashion | Premium Inventory',
      campaign_type: 'deal',
      is_running: true,
      budget_eur: 125000.50,
      cpm_eur: 2.45,
      runtime_end: '2025-07-24',
      buyer: 'DENTSU_AEGIS < Easymedia_rtb (Seat 608194)'
    }
  ],

  // Analytics data for dashboard testing
  analyticsData: {
    summary: {
      total_campaigns: 150,
      total_deals: 75,
      running_campaigns: 45,
      completed_campaigns: 180,
      total_budget_eur: 5500000.00,
      average_cpm_eur: 2.15
    },
    budgetDistribution: {
      by_campaign_type: {
        campaigns: 3200000.00,
        deals: 2300000.00
      },
      by_month: [
        { month: 'Jan', budget: 450000 },
        { month: 'Feb', budget: 520000 },
        { month: 'Mar', budget: 680000 }
      ]
    }
  }
}

// Test environment detection
process.env.NODE_ENV = 'test'
process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:3001/api/v1'

/**
 * DISCOVERY TDD HELPER FUNCTIONS
 *
 * These utilities support discovery-driven component testing
 * where behavior and requirements emerge through iteration.
 */

/**
 * Helper for testing async component state changes
 * Useful for discovery testing where we're learning about async behavior
 */
export const waitForAsyncStateChange = async (callback: () => void, timeout = 3000) => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now()

    const checkState = () => {
      try {
        callback()
        resolve(true)
      } catch (error) {
        if (Date.now() - startTime > timeout) {
          reject(new Error(`Async state change timeout after ${timeout}ms: ${error}`))
        } else {
          setTimeout(checkState, 100)
        }
      }
    }

    checkState()
  })
}

/**
 * Helper for mocking API responses during discovery testing
 * Allows rapid experimentation with different data scenarios
 */
export const mockApiResponse = (endpoint: string, response: any, status = 200) => {
  server.use(
    rest.get(`*${endpoint}`, (req, res, ctx) => {
      return res(ctx.status(status), ctx.json(response))
    })
  )
}

/**
 * Helper for testing component error boundaries
 * Useful for discovering error handling requirements
 */
export const triggerErrorBoundary = (component: any, error: Error) => {
  const originalError = console.error
  console.error = jest.fn()

  // Trigger error in component
  throw error

  console.error = originalError
}

// Export test utilities for use in test files
export * from '@testing-library/react'
export * from '@testing-library/user-event'
export { server } from './mocks/server'

/**
 * USAGE GUIDE FOR UI-DESIGN-EXPERT:
 *
 * DISCOVERY TDD PATTERNS:
 *
 * 1. Component Behavior Discovery:
 *    - Start with user interaction tests
 *    - Use screen.debug() to understand rendering
 *    - Test one behavior at a time
 *
 * 2. API Integration Discovery:
 *    - Use mockApiResponse() to test different data scenarios
 *    - Test loading states and error conditions
 *    - Discover required error handling patterns
 *
 * 3. Responsive Design Discovery:
 *    - Use toBeResponsive() matcher
 *    - Test different viewport sizes
 *    - Discover breakpoint requirements
 *
 * 4. Chart Component Discovery:
 *    - Use toRenderChartData() matcher
 *    - Test data transformation logic separately
 *    - Discover accessibility requirements
 *
 * 5. Async Behavior Discovery:
 *    - Use waitForAsyncStateChange() for complex async flows
 *    - Test timeout scenarios
 *    - Discover loading and error state requirements
 *
 * EXAMPLE TEST PATTERNS:
 *
 * // Discovery-driven component test
 * test('should discover dashboard layout requirements', async () => {
 *   render(<Dashboard />)
 *
 *   // Discover what elements should be present
 *   expect(screen.getByRole('main')).toBeInTheDocument()
 *
 *   // Discover responsive behavior
 *   expect(screen.getByTestId('dashboard-grid')).toBeResponsive()
 * })
 *
 * // API integration discovery test
 * test('should discover campaign data display requirements', async () => {
 *   mockApiResponse('/campaigns', global.testData.sampleCampaigns)
 *
 *   render(<CampaignList />)
 *
 *   // Discover how campaigns should be displayed
 *   await waitFor(() => {
 *     expect(screen.getByText(/2025_10147_0303_1_PV Promotion/)).toBeInTheDocument()
 *   })
 * })
 */