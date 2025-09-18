# Error Boundary Testing Patterns for Analytical Dashboards

## Educational TDD Documentation

This document explains the comprehensive error boundary testing patterns implemented for the PPV System Health Monitor dashboard. It serves as both implementation guidance and educational material for test-driven development in analytical dashboard contexts.

## Table of Contents

1. [Core Testing Philosophy](#core-testing-philosophy)
2. [Error Boundary Architecture](#error-boundary-architecture)
3. [Testing Patterns Overview](#testing-patterns-overview)
4. [Component Distinction](#component-distinction)
5. [Educational TDD Workflow](#educational-tdd-workflow)
6. [Implementation Guidance](#implementation-guidance)
7. [Integration with Existing Systems](#integration-with-existing-systems)

---

## Core Testing Philosophy

### Discovery-Driven Error Handling

Unlike generic applications, analytical dashboards require **discovery-driven error handling** that preserves analytical value even during failures. Our testing approach focuses on:

```
Traditional Error Handling:    →    Analytical Error Handling:
├─ Show generic error message       ├─ Preserve partial data
├─ Offer basic retry               ├─ Suggest alternative analysis
├─ Log technical details           ├─ Provide context-aware recovery
└─ Reset to initial state         └─ Maintain analytical workflow
```

### Key Testing Principles

1. **Analytical Value Preservation**: Tests ensure that even during errors, users can continue their analysis with available data
2. **Context-Aware Recovery**: Error handling adapts to user role, workflow context, and data availability
3. **Progressive Disclosure**: Technical details are available but not overwhelming for business users
4. **Workflow Continuity**: Error recovery maintains user's analytical context and state

---

## Error Boundary Architecture

### Component Responsibility Matrix

| Component | Purpose | Error Types | Recovery Strategy |
|-----------|---------|-------------|------------------|
| **DashboardErrorBoundary** | Catch JavaScript rendering errors | Runtime errors, component crashes, memory issues | Component isolation, retry, dashboard refresh |
| **AnalyticalErrorDisplay** | Display data loading failures | API errors, parsing errors, calculation failures | Alternative analysis, data export, contextual guidance |
| **useCampaignAnalysis** | Handle API integration errors | Network failures, timeout, authentication | Automatic retry, data preservation, graceful degradation |

### Error Flow Architecture

```
User Action
    ↓
┌─────────────────────────────────────┐
│ 1. API Call (useCampaignAnalysis)   │ ← Network/API Errors
├─────────────────────────────────────┤
│ 2. Data Processing & Validation     │ ← Data Quality Errors
├─────────────────────────────────────┤
│ 3. Component Rendering              │ ← JavaScript Runtime Errors
├─────────────────────────────────────┤
│ 4. Chart/Visualization Rendering    │ ← Visualization Library Errors
└─────────────────────────────────────┘
    ↓
Error Boundary Catches & Handles
    ↓
┌─────────────────────────────────────┐
│ Context-Aware Error Display         │
├─ Preserve Available Data            │
├─ Suggest Alternative Workflows      │
├─ Provide Recovery Actions           │
└─ Maintain Analytical Context        │
```

---

## Testing Patterns Overview

### Pattern 1: Error Boundary Structure Testing

**Purpose**: Ensure error boundaries exist and can catch different error types

```typescript
// Example Test Pattern
test('should catch JavaScript errors during component rendering', () => {
  render(
    <DashboardErrorBoundary>
      <ComponentThatThrows />
    </DashboardErrorBoundary>
  )

  // Verify error is caught and fallback UI is shown
  expect(screen.getByTestId('error-boundary-fallback')).toBeInTheDocument()
  expect(screen.queryByTestId('failing-component')).not.toBeInTheDocument()
})
```

**Learning Objective**: Document that error boundaries must catch errors and prevent application crashes while providing meaningful fallback UI.

### Pattern 2: Analytical Workflow Preservation Testing

**Purpose**: Ensure partial functionality remains available during errors

```typescript
// Example Test Pattern
test('should preserve campaign data when analytics charts fail', () => {
  render(
    <DashboardErrorBoundary fallbackStrategy="preserve-data">
      <CampaignDataTable data={mockCampaigns} />
      <ChartComponentThatThrows />
    </DashboardErrorBoundary>
  )

  // Campaign data should still be accessible
  expect(screen.getByTestId('campaign-data-table')).toBeInTheDocument()
  // Chart error should be contained
  expect(screen.getByText(/charts temporarily unavailable/i)).toBeInTheDocument()
})
```

**Learning Objective**: Show how error boundaries can provide granular error isolation while preserving analytical value.

### Pattern 3: Context-Aware Recovery Testing

**Purpose**: Verify that error handling adapts to analytical context

```typescript
// Example Test Pattern
test('should adapt messaging based on user role and context', () => {
  render(
    <AnalyticalErrorDisplay
      error={dataProcessingError}
      userRole={'product-manager'}
      workflowContext={{ type: 'fulfillment-analysis' }}
    />
  )

  // Should show role-appropriate messaging
  expect(screen.getByText(/issue loading your campaign analysis/i)).toBeInTheDocument()
  // Should suggest workflow-appropriate recovery
  expect(screen.getByRole('button', { name: /try basic analysis/i })).toBeInTheDocument()
})
```

**Learning Objective**: Demonstrate how error messaging should adapt to user needs and analytical context.

### Pattern 4: Progressive Disclosure Testing

**Purpose**: Ensure technical details are available without overwhelming users

```typescript
// Example Test Pattern
test('should provide progressive disclosure of error details', () => {
  render(
    <AnalyticalErrorDisplay
      error={complexError}
      technicalDetails={detailedErrorInfo}
    />
  )

  // Simple message shown by default
  expect(screen.getByText('Unable to calculate metrics')).toBeInTheDocument()
  expect(screen.queryByText(/stack trace/i)).not.toBeInTheDocument()

  // Technical details available on request
  fireEvent.click(screen.getByRole('button', { name: /technical details/i }))
  expect(screen.getByText(/error code: CALC_001/i)).toBeInTheDocument()
})
```

**Learning Objective**: Show how to balance simple user messaging with detailed technical information.

---

## Component Distinction

### DashboardErrorBoundary vs AnalyticalErrorDisplay

| Aspect | DashboardErrorBoundary | AnalyticalErrorDisplay |
|--------|------------------------|------------------------|
| **Error Types** | JavaScript runtime errors, component crashes | API failures, data processing errors |
| **Trigger** | Automatic (componentDidCatch) | Manual (error prop passed) |
| **Scope** | Component tree protection | Data/workflow error communication |
| **Recovery** | Component retry, dashboard refresh | Alternative analysis, data export |
| **Integration** | React error boundary lifecycle | Props-based error state display |

### When to Use Each Component

```typescript
// Use DashboardErrorBoundary for:
<DashboardErrorBoundary>
  <ExpensiveChartComponent data={complexData} />  // Might crash on bad data
  <CustomVisualization config={userConfig} />     // Might have runtime errors
</DashboardErrorBoundary>

// Use AnalyticalErrorDisplay for:
const { campaigns, error } = useCampaignAnalysis()
if (error) {
  return <AnalyticalErrorDisplay error={error} partialData={campaigns} />
}
```

---

## Educational TDD Workflow

### Phase 1: RED - Failing Tests Document Requirements

1. **Create failing tests** that document exactly how error handling should work
2. **Focus on user experience** rather than technical implementation
3. **Test different error scenarios** relevant to analytical workflows
4. **Document recovery workflows** that preserve analytical value

```bash
# Run failing tests to see documented requirements
npm test DashboardErrorBoundary.test.tsx
npm test AnalyticalErrorDisplay.test.tsx
```

### Phase 2: GREEN - Minimal Implementation

1. **Create basic component structure** to make tests pass
2. **Implement core error catching** (for error boundaries)
3. **Add basic error display** (for error display components)
4. **Focus on making tests pass** without optimization

### Phase 3: REFACTOR - Optimize and Enhance

1. **Extract reusable patterns** into hooks or utilities
2. **Add performance optimizations** (memoization, etc.)
3. **Enhance user experience** with animations, better messaging
4. **Add integration with monitoring** and logging systems

### Discovery Questions for Implementation

During each phase, ask these discovery questions:

**RED Phase Questions:**
- What specific error scenarios do product managers encounter?
- How should partial data be presented during errors?
- What recovery actions provide the most analytical value?
- How should error messaging adapt to different user roles?

**GREEN Phase Questions:**
- What's the minimal implementation that satisfies user needs?
- How can we catch errors without impacting performance?
- What fallback UI provides the best user experience?
- How do we integrate with existing dashboard components?

**REFACTOR Phase Questions:**
- How can we extract reusable error handling patterns?
- What performance optimizations maintain responsiveness?
- How can we improve error messaging based on user feedback?
- What monitoring data helps improve error handling?

---

## Implementation Guidance

### DashboardErrorBoundary Implementation Steps

1. **Create Error Boundary Class Component**
```typescript
class DashboardErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // Log error with analytical context
    this.logErrorWithContext(error, errorInfo)
  }
}
```

2. **Add Analytical Context Logging**
```typescript
logErrorWithContext(error, errorInfo) {
  const analyticalContext = {
    currentCampaigns: this.props.currentCampaigns,
    activeFilters: this.props.activeFilters,
    analysisView: this.props.analysisView,
    userRole: this.props.userRole
  }

  console.error('DashboardErrorBoundary caught error:', {
    error: error.toString(),
    errorInfo,
    analyticalContext,
    timestamp: new Date().toISOString()
  })
}
```

3. **Create Fallback UI with Recovery Options**
```typescript
render() {
  if (this.state.hasError) {
    return (
      <ErrorBoundaryFallback
        error={this.state.error}
        onRetry={() => this.setState({ hasError: false })}
        onRefreshDashboard={this.props.onRefreshDashboard}
        onExportData={this.props.onExportData}
        section={this.props.section}
      />
    )
  }

  return this.props.children
}
```

### AnalyticalErrorDisplay Implementation Steps

1. **Create Functional Component with Error Prop**
```typescript
const AnalyticalErrorDisplay: React.FC<AnalyticalErrorDisplayProps> = ({
  error,
  partialData,
  userRole,
  workflowContext,
  onRetry,
  onExportData
}) => {
  // Component implementation
}
```

2. **Add Error Type Detection and Messaging**
```typescript
const getErrorMessage = (error, userRole) => {
  const messageMap = {
    'api-error': {
      'product-manager': 'There was an issue loading your campaign analysis',
      'analyst': 'API request failed - data may be temporarily unavailable',
      'technical-user': `API Error: ${error.code} - ${error.message}`
    },
    // ... other error types
  }

  return messageMap[error.type]?.[userRole] || error.message
}
```

3. **Add Recovery Action Suggestions**
```typescript
const getRecoveryActions = (error, partialData, workflowContext) => {
  const baseActions = []

  if (error.retryable) {
    baseActions.push({ type: 'retry', label: 'Retry Loading Data' })
  }

  if (partialData?.length > 0) {
    baseActions.push({ type: 'view-partial', label: 'View Available Data' })
    baseActions.push({ type: 'export', label: 'Export Partial Data' })
  }

  // Add context-specific actions based on workflow
  return [...baseActions, ...getWorkflowSpecificActions(workflowContext)]
}
```

---

## Integration with Existing Systems

### useCampaignAnalysis Hook Integration

The error boundaries complement the existing `useCampaignAnalysis` hook:

```typescript
// Hook handles API errors and data preservation
const { campaigns, analyticsSummary, error, loading } = useCampaignAnalysis()

// AnalyticalErrorDisplay handles error presentation
if (error) {
  return (
    <AnalyticalErrorDisplay
      error={error}
      partialData={campaigns}  // Hook preserves partial data
      onRetry={refetchData}
    />
  )
}

// DashboardErrorBoundary wraps components that might crash
return (
  <DashboardErrorBoundary>
    <ChartsSection campaigns={campaigns} analytics={analyticsSummary} />
  </DashboardErrorBoundary>
)
```

### Existing Component Reuse

```typescript
// Reuse existing ErrorMessage component patterns
import ErrorMessage from '@/components/ui/ErrorMessage'

const AnalyticalErrorDisplay = ({ error, onRetry }) => {
  return (
    <ErrorMessage
      error={getAnalyticalErrorMessage(error)}
      onRetry={onRetry}
      variant="analytical"  // New variant for analytical context
    />
  )
}
```

### Dashboard Component Integration

```typescript
// Granular error boundary placement
const Dashboard = () => {
  return (
    <main>
      <DashboardErrorBoundary section="summary">
        <SummaryCards />
      </DashboardErrorBoundary>

      <DashboardErrorBoundary section="charts">
        <ChartsSection />
      </DashboardErrorBoundary>

      <DashboardErrorBoundary section="table">
        <CampaignTable />
      </DashboardErrorBoundary>
    </main>
  )
}
```

---

## Key Learning Points

### 1. Error Boundaries vs Error Display Components

- **Error Boundaries**: Catch JavaScript errors automatically during React lifecycle
- **Error Display**: Present data/API errors with contextual recovery options
- **Both are needed**: Different error types require different handling approaches

### 2. Analytical Context Matters

- Generic error messages don't help analytical workflows
- Context-aware messaging improves user experience
- Recovery options should match analytical needs

### 3. Partial Data Has Value

- Don't hide all data when some processing fails
- Show what's available and what alternatives exist
- Maintain analytical workflow continuity

### 4. Progressive Disclosure

- Simple messages for business users
- Technical details available when needed
- Role-based messaging improves usability

### 5. Testing Drives Design

- Tests document expected behavior before implementation
- Discovery-driven testing reveals user needs
- TDD ensures error handling serves analytical workflows

---

## Testing Commands

```bash
# Run all error boundary tests
npm test ErrorBoundary

# Run specific component tests
npm test DashboardErrorBoundary.test.tsx
npm test AnalyticalErrorDisplay.test.tsx

# Run tests in watch mode during development
npm run test:watch ErrorBoundary

# Generate coverage report for error handling
npm run test:coverage -- --testPathPattern=ErrorBoundary
```

## Next Steps

1. **Implement components** following TDD methodology (RED → GREEN → REFACTOR)
2. **Add monitoring integration** to track error patterns in production
3. **Create user feedback system** to improve error messaging
4. **Develop error handling documentation** for business users
5. **Add A/B testing** for different error recovery workflows

---

*This documentation serves as both implementation guidance and educational material for test-driven development in analytical dashboard contexts. It demonstrates how TDD principles can be applied to create user-centered error handling that preserves analytical value.*