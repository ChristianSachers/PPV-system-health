/**
 * TDD Result Processor for Jest
 *
 * Custom test result processor that provides TDD-specific metrics
 * and feedback for discovery-driven development workflow
 */

module.exports = (results) => {
  // Calculate TDD-specific metrics
  const tddMetrics = {
    totalTests: results.numTotalTests,
    passedTests: results.numPassedTests,
    failedTests: results.numFailedTests,
    pendingTests: results.numPendingTests,
    coveragePercentage: results.coverageMap ?
      Math.round(results.coverageMap.getCoverageSummary().lines.pct) : 0,
    testSuites: results.testResults.length,
    discoveryTests: 0, // Tests marked with 'discovery' tag
    regressionTests: 0, // Tests that prevent regression
    integrationTests: 0 // Integration tests
  }

  // Analyze test results for TDD patterns
  results.testResults.forEach(testResult => {
    testResult.testResults.forEach(test => {
      if (test.fullName.includes('discovery') || test.fullName.includes('Discovery')) {
        tddMetrics.discoveryTests++
      }
      if (test.fullName.includes('regression') || test.fullName.includes('prevent')) {
        tddMetrics.regressionTests++
      }
      if (test.fullName.includes('integration') || test.fullName.includes('Integration')) {
        tddMetrics.integrationTests++
      }
    })
  })

  // TDD Health Score calculation
  const healthScore = calculateTDDHealthScore(tddMetrics)

  // Console output for TDD feedback
  if (process.env.NODE_ENV !== 'ci') {
    console.log('\n📊 TDD Metrics Dashboard:')
    console.log('═══════════════════════════════════════')
    console.log(`✅ Passed Tests: ${tddMetrics.passedTests}/${tddMetrics.totalTests}`)
    console.log(`❌ Failed Tests: ${tddMetrics.failedTests}`)
    console.log(`⏳ Pending Tests: ${tddMetrics.pendingTests}`)
    console.log(`📈 Coverage: ${tddMetrics.coveragePercentage}%`)
    console.log(`🔍 Discovery Tests: ${tddMetrics.discoveryTests}`)
    console.log(`🛡️  Regression Tests: ${tddMetrics.regressionTests}`)
    console.log(`🔗 Integration Tests: ${tddMetrics.integrationTests}`)
    console.log(`💪 TDD Health Score: ${healthScore}/100`)
    console.log('═══════════════════════════════════════')

    // TDD recommendations
    if (tddMetrics.failedTests > 0) {
      console.log('🔴 Red Phase: Tests are failing - implement minimal code to pass')
    } else if (tddMetrics.pendingTests > 0) {
      console.log('🟡 Amber Phase: Pending tests found - complete implementation')
    } else {
      console.log('🟢 Green Phase: All tests passing - consider refactoring')
    }

    if (tddMetrics.coveragePercentage < 70) {
      console.log('💡 Consider adding more test coverage for better regression protection')
    }

    if (tddMetrics.discoveryTests === 0) {
      console.log('🔬 Consider adding discovery tests to explore new requirements')
    }
  }

  return results
}

function calculateTDDHealthScore(metrics) {
  let score = 0

  // Test pass rate (40% of score)
  const passRate = metrics.totalTests > 0 ? (metrics.passedTests / metrics.totalTests) : 0
  score += passRate * 40

  // Coverage (30% of score)
  score += (metrics.coveragePercentage / 100) * 30

  // Test diversity (30% of score)
  const hasDiscoveryTests = metrics.discoveryTests > 0 ? 10 : 0
  const hasRegressionTests = metrics.regressionTests > 0 ? 10 : 0
  const hasIntegrationTests = metrics.integrationTests > 0 ? 10 : 0
  score += hasDiscoveryTests + hasRegressionTests + hasIntegrationTests

  return Math.round(score)
}