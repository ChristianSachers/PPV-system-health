/**
 * Jest Configuration for PPV System Health Monitor Frontend
 *
 * Discovery-Driven TDD Setup:
 * - Optimized for React component testing with discovery patterns
 * - Mock service worker for API integration testing
 * - Chart testing support for analytics dashboard
 * - TypeScript support for type-safe testing
 */

const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  // Test environment
  testEnvironment: 'jsdom',

  // Setup files
  setupFilesAfterEnv: [
    '<rootDir>/src/test/setup.ts'
  ],

  // Module paths and mappings
  moduleNameMapping: {
    // Handle module aliases (if you're using them in your Next.js config)
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@/services/(.*)$': '<rootDir>/src/services/$1',
    '^@/types/(.*)$': '<rootDir>/src/types/$1',
    '^@/utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@/test/(.*)$': '<rootDir>/src/test/$1'
  },

  // File patterns
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.(ts|tsx|js|jsx)',
    '<rootDir>/src/**/*.(test|spec).(ts|tsx|js|jsx)',
    '<rootDir>/__tests__/**/*.(ts|tsx|js|jsx)'
  ],

  // Coverage configuration
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/test/**/*',
    '!src/**/*.stories.{ts,tsx}',
    '!src/**/*.config.{ts,js}',
    '!src/pages/_app.tsx',
    '!src/pages/_document.tsx'
  ],

  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },

  coverageReporters: [
    'text',
    'lcov',
    'html'
  ],

  // Transform configuration
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }]
  },

  // Module file extensions
  moduleFileExtensions: [
    'ts',
    'tsx',
    'js',
    'jsx',
    'json',
    'node'
  ],

  // Test timeout (useful for async tests)
  testTimeout: 10000,

  // Clear mocks between tests
  clearMocks: true,

  // Restore mocks after each test
  restoreMocks: true,

  // Verbose output for debugging
  verbose: false,

  // Watch plugins for better development experience
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ],

  // Global setup for canvas mocking (needed for chart testing)
  setupFiles: [
    'jest-canvas-mock',
    'whatwg-fetch'
  ],

  // Mock static file imports
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': '<rootDir>/src/test/__mocks__/fileMock.js'
  },

  // Ignore patterns
  testPathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/',
    '<rootDir>/out/',
    '<rootDir>/build/'
  ],

  // Transform ignore patterns
  transformIgnorePatterns: [
    'node_modules/(?!(recharts|d3-*)/)'
  ]
}

// TDD-specific Jest configuration for discovery-driven development
const tddEnhancedConfig = {
  ...customJestConfig,

  // Custom reporters for TDD workflow
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: 'test-results',
        outputName: 'junit.xml',
        suiteName: 'PPV System Health Monitor Frontend Tests'
      }
    ]
  ],

  // Test result processor for TDD metrics
  testResultsProcessor: '<rootDir>/src/test/processors/tddResultProcessor.js',

  // Global variables for tests
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json'
    },
    __DEV__: true,
    __TEST__: true
  }
}

// Create and export the Jest configuration
module.exports = createJestConfig(tddEnhancedConfig)

/**
 * USAGE GUIDE FOR UI-DESIGN-EXPERT:
 *
 * BASIC TESTING COMMANDS:
 * - npm test                    # Run all tests once
 * - npm run test:watch         # Run tests in watch mode (TDD style)
 * - npm run test:coverage      # Run tests with coverage report
 * - npm run test:ci           # Run tests in CI mode
 *
 * TDD WORKFLOW:
 * 1. Write a failing test (Red)
 * 2. Run: npm run test:watch
 * 3. Implement minimal code to pass (Green)
 * 4. Refactor while keeping tests green (Refactor)
 *
 * DISCOVERY TESTING PATTERNS:
 * - Use describe() blocks to group related discovery scenarios
 * - Use test.each() for parametrized testing of different data scenarios
 * - Use screen.debug() to understand component rendering during development
 * - Use userEvent for realistic user interaction testing
 *
 * COMPONENT TESTING STRATEGY:
 * - Test component behavior, not implementation details
 * - Focus on user interactions and visual feedback
 * - Mock API calls using MSW (Mock Service Worker)
 * - Test responsive behavior and accessibility
 *
 * CHART TESTING APPROACH:
 * - Test data transformation logic separately from chart rendering
 * - Mock Recharts components for unit tests
 * - Test chart interactions (hover, click, zoom)
 * - Validate chart accessibility features
 *
 * ASYNC TESTING PATTERNS:
 * - Use waitFor() for async state changes
 * - Use findBy* queries for elements that appear asynchronously
 * - Test loading states and error handling
 * - Mock API responses with MSW for integration testing
 */