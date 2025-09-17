# PRD: PPV System Health Monitor
*Discovery-Driven Development - Requirements will evolve through exploration*

## Introduction/Overview

The PPV System Health Monitor is a forensic analysis tool designed to investigate and understand the fulfillment performance of our programmatic public video ad serving system. Rather than managing active campaigns, this tool performs retrospective analysis on completed campaigns and deals to identify system performance patterns, bottlenecks, and improvement opportunities.

**Core Problem:** Currently, there is no transparency into whether our ad serving system achieves optimal campaign fulfillment. We need to establish baseline performance metrics and discover patterns that indicate system health issues.

**Target User:** Product Manager with deep PPV domain knowledge and CS background, requiring visual data exploration tools with clickable insights for deeper investigation.

## Discovery Goals

### Primary Hypotheses to Test:
1. **100% Fulfillment Hypothesis:** Guaranteed campaigns and deals should achieve 100% impression delivery when sufficient opportunity exists
2. **DSP Interference Hypothesis:** Deal underperformance may correlate with DSP bidding cessation rather than system failures
3. **Opportunity vs. Performance Hypothesis:** System failures can be proven by demonstrating adequate inventory opportunity existed but wasn't utilized
4. **Pattern Recognition Hypothesis:** Underperformance patterns exist across temporal, geographic, or campaign parameter dimensions

### Learning Success Criteria:
- Ability to prove when system had adequate opportunity but failed to deliver 100% fulfillment
- Clear identification of guaranteed vs. unguaranteed performance gaps
- Discovery of actionable patterns that point to specific system improvements
- Establishment of quantitative baseline for future system performance comparison

## Investigation Workflows

### Phase 1: Overall Health Assessment (Weeks 1-2)
**Visual Learning Journey:**
```
Upload Campaign Data → Validate & Clean → Generate System Overview
        ↓                    ↓                      ↓
   XLSX Processing    →  Data Quality Check  →  Baseline Dashboard
```

**Key Investigation Paths:**
1. **System Baseline Discovery:** Visual dashboard showing overall fulfillment rates across 7-day, 30-day, and yearly time windows
2. **Guaranteed vs. Unguaranteed Gap Analysis:** Comparative performance visualization with absolute and percentage metrics
3. **Campaign/Deal Distribution Analysis:** Understanding the volume and variety of campaigns in the system

### Phase 2: Temporal Trend Analysis (Weeks 3-4)
**Rolling Window Investigation:**
- Trend detection across multiple time granularities
- Performance change correlation with system modifications
- Seasonal or cyclical pattern identification

### Phase 3: Performance Segmentation (Weeks 5-6)
**Guaranteed vs. Unguaranteed Deep Dive:**
- DSP bidding cessation impact analysis
- Performance distribution analysis within each category
- Outlier identification and characterization

### Phase 4: Geographic/Site Performance Patterns (Weeks 7+)
**Site-Level Forensics:**
- Performance correlation with site characteristics
- Geographic performance pattern discovery
- Inventory opportunity vs. utilization analysis

## Analytical Requirements

### Flexible Data Integration Framework:
1. **Campaign Data Import System:**
   - XLSX file upload with validation and error reporting
   - UUID-based deduplication and incremental updates
   - Campaign/Deal classification logic based on business rules

2. **API Integration Layer:**
   - Bearer token session management
   - Flexible query parameter system for different analysis granularities
   - Data aggregation and correlation capabilities

3. **Historical Data Persistence:**
   - Session-independent data storage
   - Incremental data updates without duplication
   - Data integrity maintenance across uploads

### Visual Exploration Tools:
1. **Interactive Dashboard Framework:**
   - Clickable elements that drill down into deeper analysis
   - Multiple visualization types (trends, distributions, comparisons)
   - Filter and segment capabilities across multiple dimensions

2. **Pattern Discovery Interface:**
   - Comparative analysis tools (actual vs. goal performance)
   - Outlier identification and highlighting
   - Correlation analysis between different data dimensions

3. **Insight Generation System:**
   - Automated underperformance flagging based on configurable thresholds
   - Campaign/Deal performance ranking and categorization
   - Opportunity analysis (inventory availability vs. utilization)

## Discovery Constraints

### Safe Exploration Boundaries:
- **Historical Data Only:** No real-time components or live campaign modifications
- **Read-Only Analysis:** No data modification capabilities, only aggregation and visualization
- **Completed Campaigns Only:** Analysis restricted to campaigns/deals past their end date with complete data
- **Single User System:** No multi-user management or authentication requirements

### Data Integrity Safeguards:
- UUID immutability for campaign/deal identification
- Validation of data completeness before analysis inclusion
- Clear differentiation between campaigns and deals based on buyer field logic

## Investigation Framework

### Hypothesis Testing Methodology:
1. **Baseline Establishment:** Quantify current fulfillment performance across all dimensions
2. **Pattern Recognition:** Identify statistical outliers and performance clusters
3. **Correlation Analysis:** Test relationships between performance and various campaign/deal attributes
4. **Opportunity Analysis:** Compare delivered impressions against available inventory opportunities

### Data Exploration Safety:
- All analysis performed on static historical datasets
- No impact on live ad serving system
- Comprehensive data validation before analysis inclusion

## Technical Foundation

### Core Infrastructure Requirements:
1. **Data Processing Pipeline:**
   - XLSX parsing and validation
   - API data integration and aggregation
   - UUID-based relationship management between campaign and reporting data

2. **Analytical Database:**
   - Historical campaign and performance data storage
   - Optimized for analytical queries across multiple dimensions
   - Session-independent data persistence

3. **Visualization Engine:**
   - Interactive dashboard framework
   - Multiple chart types and filtering capabilities
   - Drill-down functionality for detailed investigation

### Integration Specifications:
- **Campaign Data:** XLSX file format with predefined schema
- **Reporting Data:** REST API with bearer token authentication
- **Time Granularity:** Hourly reporting data aggregated to various time windows
- **Geographic Granularity:** Site-level performance analysis capabilities

## Learning Success Metrics

### Discovery Milestones:
1. **Baseline Established:** Clear quantification of current system performance
2. **Pattern Identification:** Discovery of actionable performance patterns
3. **Problem Proof Capability:** Ability to demonstrate system failures with supporting data
4. **Improvement Framework:** Data-driven recommendations for system enhancements

### Analytical Capabilities Delivered:
- Visual comparison of guaranteed vs. unguaranteed performance
- Temporal trend analysis with configurable time windows
- Site and geographic performance pattern recognition
- Campaign/Deal underperformance identification and analysis

## Implementation Iterations

### Value-Driven Development Approach

The PPV System Health Monitor will be built through iterative development cycles, with each iteration delivering immediate value to the product manager. This approach enables early feedback, reduces risk, and ensures each development phase produces a working application that provides analytical insights.

### Iteration Sequence

#### **Iteration 1: Basic Campaign Data Foundation** 🏗️
**Business Value:** PM can upload XLSX campaign files and see structured, validated campaign data
**User Capability:** Upload campaigns, view data quality reports, browse campaign information
**Deliverables:**
- XLSX file upload system with validation
- Campaign data storage and persistence
- Basic campaign data display interface
- Data quality reporting (excluded records, validation errors)

**Technical Artifacts:** `tasks-iteration1-campaign-data-foundation.md`

#### **Iteration 2: API Integration & Fulfillment Analysis** 🔌📊
**Business Value:** PM can assess actual campaign performance vs goals using real reporting data
**User Capability:** Connect to reporting API, calculate fulfillment rates, identify underperforming campaigns
**Deliverables:**
- Bearer token API integration for reporting data
- Fulfillment percentage calculations (delivered vs goal impressions)
- Performance indicators (red/green status based on fulfillment thresholds)
- Campaign vs Deal classification logic based on buyer field

**Technical Artifacts:** `tasks-iteration2-api-integration-fulfillment.md`

#### **Iteration 3: System Health Triage Dashboard** 🚨
**Business Value:** PM can assess overall system health and identify problem categories at a glance
**User Capability:** View system-wide performance metrics, filter by guaranteed vs unguaranteed, identify categories needing attention
**Deliverables:**
- Level 1 navigation interface (System Health Overview)
- Guaranteed vs Unguaranteed performance breakdown
- Time window filters (7-day, 30-day, yearly)
- Category-based investigation entry points

**Technical Artifacts:** `tasks-iteration3-system-health-triage.md`

#### **Iteration 4: Problem Investigation Interface** 🔍
**Business Value:** PM can drill down to see specific underperforming campaigns/deals requiring attention
**User Capability:** Navigate from system overview to specific problem identification, focus on actionable underperformance
**Deliverables:**
- Level 2-3 navigation (Category Analysis → Problem Investigation)
- Underperforming campaign/deal identification and ranking
- Shortfall calculations and severity classification
- Click-through navigation for detailed analysis

**Technical Artifacts:** `tasks-iteration4-problem-investigation.md`

#### **Iteration 5: Temporal Trend Analysis** 📈
**Business Value:** PM can see if system performance is improving or declining over time
**User Capability:** Analyze performance trends, identify system degradation or improvement patterns
**Deliverables:**
- Rolling window performance analysis
- Trend indicators (improving/declining/stable)
- Comparative time period analysis
- Performance change correlation identification

**Technical Artifacts:** `tasks-iteration5-temporal-trend-analysis.md`

#### **Iteration 6: Forensic Root Cause Analysis** 🔬
**Business Value:** PM can investigate specific campaign failures with granular site and time breakdowns
**User Capability:** Perform detailed forensic analysis of underperforming campaigns, identify specific bottlenecks
**Deliverables:**
- Level 4 navigation (Individual Campaign Forensic Analysis)
- Custom date/hour picker for precise timeframe analysis
- Site-level performance breakdown and analysis
- Root cause insight generation and recommendations

**Technical Artifacts:** `tasks-iteration6-forensic-root-cause-analysis.md`

### Iteration Dependencies and Flow

```
Iteration 1 (Data Foundation)
    ↓
Iteration 2 (Performance Analysis) ← Requires API integration
    ↓
Iteration 3 (System Health Dashboard) ← Requires fulfillment calculations
    ↓
Iteration 4 (Problem Investigation) ← Requires system health metrics
    ↓
Iteration 5 (Trend Analysis) ← Requires historical performance data
    ↓
Iteration 6 (Forensic Analysis) ← Requires all previous capabilities
```

### Value Validation Criteria

Each iteration must demonstrate:
- **Immediate Usability:** PM can perform meaningful analysis with current functionality
- **Incremental Value:** New capabilities build on previous iterations without breaking existing functionality
- **Discovery Enablement:** Each iteration reveals new insights that inform subsequent development priorities
- **Stakeholder Readiness:** Interface quality suitable for executive presentations and decision-making

## Evolution Plan

### Requirements Evolution Framework:
This PRD will be updated iteratively as discoveries emerge:

**Phase 1 Learnings → Phase 2 Requirements:**
- Baseline analysis results will inform deeper investigation priorities
- Pattern discoveries will drive new analytical tool requirements
- User interaction patterns will guide UI/UX refinements

**Expected Requirement Evolution Areas:**
1. **Additional Data Dimensions:** New correlation factors based on discovered patterns
2. **Advanced Analytics:** Statistical analysis tools based on pattern complexity
3. **Automated Insights:** Pattern recognition automation based on manual discovery success
4. **Reporting Capabilities:** Stakeholder communication tools based on insight generation

### Iterative Development Approach:
- **2-Week Discovery Sprints:** Each development cycle focuses on one investigation phase
- **Learning-Driven Pivots:** Requirements adjustments based on analytical discoveries
- **User Feedback Integration:** PM insights drive next iteration priorities
- **Capability Expansion:** New analytical tools added based on proven investigation needs

## Open Hypotheses

### Areas for Future Exploration:
1. **Site Performance Correlation:** What site characteristics predict performance issues?
2. **Temporal Pattern Analysis:** Do performance issues correlate with specific time periods or events?
3. **Campaign Parameter Impact:** How do different campaign configurations affect fulfillment success?
4. **Inventory Optimization:** Can we identify optimal campaign-to-inventory matching patterns?
5. **DSP Behavior Analysis:** What patterns exist in DSP bidding behavior that affect deal performance?

### Investigation Questions to Resolve:
- What constitutes "adequate opportunity" for fulfillment measurement?
- How should we weight different underperformance factors for prioritization?
- What time windows provide the most meaningful trend analysis?
- How can we automate the identification of system improvement opportunities?

---

**Note:** This PRD follows discovery-driven development principles. Requirements will evolve based on analytical discoveries and user learning. Each development iteration should focus on enabling the next level of investigation rather than implementing rigid specifications.