# PPV System Health Monitor - Architecture Decisions

*Living document capturing key architectural decisions and reasoning*
*Last Updated: 2025-09-17*

## Overview

This document captures the architectural decisions made for the PPV System Health Monitor, a discovery-driven forensic analysis tool for investigating impression delivery fulfillment performance. Each decision includes context, alternatives considered, and reasoning.

**CRITICAL CORRECTION:** All architecture decisions reflect FULFILLMENT ANALYSIS focus (delivered impressions vs impression goals), NOT budget/CPM optimization.

---

## AD-001: Discovery-Driven Development Architecture

**Decision:** Build flexible analytical tools rather than rigid feature specifications

**Context:**
- Requirements will evolve as patterns are discovered through data exploration
- User is a PM with deep domain knowledge but 10+ years away from coding
- System is exploratory by nature - "establish baseline then dig deeper"

**Alternatives Considered:**
- Traditional feature-based development
- Fully specified requirements upfront

**Reasoning:**
- Explicit statement: "exact scope is not 100% clear at project start"
- Investigation priorities will emerge from initial discoveries
- Need maximum flexibility for changing analytical requirements

**Implications:**
- Component architecture must support rapid iteration
- Data models should be extensible
- UI components should be composable and reusable

---

## AD-002: Real-Time Data Aggregation Strategy

**Decision:** Real-time fulfillment aggregation over pre-computed summaries

**Context:**
- Need to analyze impression delivery fulfillment across multiple time granularities (7-day, 30-day, yearly)
- ~300 campaigns maximum, manageable dataset size for fulfillment calculations
- Discovery-driven fulfillment analysis requires flexible data slicing of impression delivery rates

**Alternatives Considered:**
```
Option A: Pre-compute Everything
├─ Pros: Fast dashboard loading
├─ Cons: Large storage, complex updates, inflexible
└─ Example: Store 7-day, 30-day, yearly summaries

Option B: Real-time Aggregation (CHOSEN)
├─ Pros: Flexible queries, always current, extensible
├─ Cons: Slower performance, complex queries
└─ Example: Calculate on-demand from hourly data
```

**Reasoning:**
- Dataset size is manageable (~300 campaigns, hourly granularity) for fulfillment calculations
- Fulfillment discovery workflow requires flexible filtering and slicing of impression delivery data
- New fulfillment analytical dimensions will emerge - pre-computation too rigid
- Modern databases handle impression delivery aggregations efficiently at this scale

**Implications:**
- Database queries must be optimized for fulfillment calculation workloads (delivered_impressions / impression_goal)
- Caching strategy needed for frequently accessed fulfillment aggregations
- Fulfillment query complexity will be higher but more flexible for discovery analysis

---

## AD-003: Modern Visualization Framework

**Decision:** Use modern framework (Chart.js/D3.js) over custom visualization components

**Context:**
- User is visual learner requiring rich interactive dashboards
- Need click-to-drill-down functionality
- Professional appearance important for stakeholder trust

**Alternatives Considered:**
- Custom visualization components
- Server-side generated charts
- Simple HTML tables with basic styling

**Reasoning:**
- Rich interactions required (click-through navigation, hover details)
- Professional appearance critical for PM presenting to stakeholders
- Time-to-market considerations favor proven frameworks
- Interactive features (zoom, filter, drill-down) built-in

**Technical Choice:** Chart.js for standard charts, with D3.js for custom visualizations if needed

**Implications:**
- Frontend framework must support rich chart libraries
- Bundle size considerations for chart libraries
- Learning curve for team on chart configuration

---

## AD-004: Hybrid Development Approach

**Decision:** Start simple, add complexity based on discoveries

**Context:**
- 1-year application lifecycle
- Discovery-driven requirements evolution
- Need to balance functionality with development speed

**Development Phases:**
1. **Phase 1:** Basic fulfillment gap analysis
2. **Phase 2:** Temporal trend analysis
3. **Phase 3:** Advanced drill-down and correlation analysis
4. **Phase 4:** Automated pattern detection (if needed)

**Reasoning:**
- Aligns with discovery-driven development principles
- Provides early value while building toward complex analytics
- Allows requirement validation before heavy investment
- Tactical solution approach matches business timeline

**Implications:**
- Component architecture must support feature addition without refactoring
- Database schema should be extensible
- UI design must accommodate new analytical tools

---

## AD-005: Component Architecture Structure

**Decision:** React-based modular dashboard architecture

**Component Hierarchy:**
```
DashboardApp
├── FilterBar (Performance threshold, Guaranteed/Unguaranteed)
├── FulfillmentGapAnalysis (Primary visualization)
├── TemporalTrendAnalysis (Secondary visualization)
├── DrillDownModal (Detailed campaign analysis)
└── DataAggregationService (Real-time query engine)
```

**Context:**
- Need flexible, composable UI components
- Multiple visualization types with shared filtering
- Drill-down navigation between analysis levels

**Reasoning:**
- React provides component reusability for evolving requirements
- Modular structure supports hybrid development approach
- Clear separation between data aggregation and visualization
- Service layer abstracts database complexity from UI components

**Implications:**
- State management needed for shared filters and drill-down context
- API design must support component-level data requirements
- Component props must be designed for extensibility

---

## AD-006: Visual Design Patterns

**Decision:** Color-coded fulfillment indicators with impression delivery trend analysis

**Visual Language:**
- **Fulfillment Color Coding:** 🟢 ≥100% (Goal Met/Exceeded) | 🟡 98-99.9% (Near Goal) | 🟠 95-98% (Moderate Shortfall) | 🔴 <95% (Critical Shortfall)
- **Interaction Pattern:** Click anywhere to drill down into fulfillment details
- **Trend Indicators:** ↗ Improving Fulfillment | ↘ Declining Fulfillment | → Stable Fulfillment

**Context:**
- User is visual learner who needs immediate fulfillment pattern recognition
- Prefers "lazy" shortcuts and clickable insights for impression delivery analysis
- Professional PM background requires executive-ready fulfillment visualizations

**Reasoning:**
- Color coding enables instant fulfillment assessment (delivered vs goal)
- Trend lines show impression delivery performance changes over time
- Click-to-drill-down reduces fulfillment investigation complexity
- Professional appearance suitable for stakeholder fulfillment presentations

**Implications:**
- Consistent color scheme across all visualizations
- Accessibility considerations for color-blind users
- Hover states and visual feedback for interactive elements

---

## AD-007: Discovery Priority Sequence

**Decision:** Impression delivery gaps first, then temporal trends, then detailed analysis

**Investigation Sequence:**
1. **Primary:** Impression Delivery Gap Analysis (Guaranteed vs Unguaranteed fulfillment rates)
2. **Secondary:** Temporal Fulfillment Trend Analysis (Rolling impression delivery windows)
3. **Tertiary:** Geographic/Site Fulfillment Patterns
4. **Advanced:** Campaign-specific fulfillment forensic analysis

**Context:**
- User explicitly stated priority preferences
- Aligns with business goal: "establish baseline then dig deeper"
- PM needs to prove system performance issues exist

**Reasoning:**
- Fulfillment gaps directly address core business question
- Temporal trends show if system is improving or degrading
- Geographic patterns help identify systematic issues
- Sequence builds from general to specific investigation

**Implications:**
- Development sprint planning follows this priority order
- Data models should optimize for fulfillment gap queries first
- UI navigation should support this natural investigation flow

---

## AD-008: Data Filtering Strategy

**Decision:** Performance threshold and guaranteed/unguaranteed filtering as primary filters

**Filter Types:**
- **Performance Threshold:** Show campaigns below X% fulfillment
- **Purchase Type Filter:** Guaranteed vs Unguaranteed campaigns
- **Time Window Filter:** 7-day, 30-day, yearly analysis periods

**Context:**
- ~300 campaigns need efficient filtering for pattern discovery
- User specifically mentioned these as key analytical dimensions
- Guaranteed campaigns have different performance expectations

**Reasoning:**
- Performance threshold filtering directly supports underperformance investigation
- Purchase type separation critical for different fulfillment expectations
- Time windows enable trend analysis at different scales
- Keeps UI simple while providing powerful analytical capability

**Implications:**
- Database indexes needed for performance and purchase_type fields
- Filter state must persist during drill-down navigation
- Query optimization required for filtered aggregations

---

## AD-009: Four-Level Drill-Down Navigation

**Decision:** Structured drill-down from system overview to hourly site analysis

**Navigation Levels:**
```
Level 1: System Overview (30-day summary)
         ↓ (Click campaign category)
Level 2: Campaign Categories (Guaranteed vs Unguaranteed)
         ↓ (Click individual campaign)
Level 3: Individual Campaigns (Performance details)
         ↓ (Click time/site analysis)
Level 4: Site/Time Analysis (Hourly breakdowns)
```

**Context:**
- User needs to move from high-level patterns to specific problem identification
- Investigation workflow: overview → category → specific → forensic detail
- PM needs to identify specific campaigns for system improvement focus

**Reasoning:**
- Matches natural analytical thinking progression
- Each level provides actionable insights at appropriate granularity
- Supports both quick overview and detailed investigation needs
- Aligns with discovery-driven exploration methodology

**Implications:**
- Navigation state management across drill-down levels
- Data aggregation requirements for each level
- UI design must support intuitive back-navigation
- Performance optimization for detailed level queries

---

## AD-010: Critical Data Structure Architecture

**Decision:** Impression-focused database schema with correct field types

**CRITICAL DATA STRUCTURE SPECIFICATIONS:**

**Campaign/Deal Table Schema:**
```sql
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    impression_goal INTEGER NOT NULL CHECK (impression_goal BETWEEN 1 AND 2000000000),
    runtime TEXT NOT NULL,  -- Format: "START_DATE-END_DATE" or "ASAP-END_DATE"
    buyer TEXT,  -- 'Not set' = campaign, other values = deal
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Context:**
- **WRONG ASSUMPTION:** impression_goal as range string, separate start/end dates
- **CORRECT REALITY:** impression_goal is concrete integer, runtime is single hyphenated field
- **WRONG FOCUS:** Budget/CPM optimization workflows
- **CORRECT FOCUS:** Fulfillment analysis (delivered_impressions / impression_goal)

**Alternatives Considered:**
```
REJECTED: Separate start_date/end_date fields
├─ Reason: Data comes as single runtime field "START-END"
├─ Example: "14.01.2025-26.01.2025" or "ASAP-14.12.2025"
└─ Impact: Would require unnecessary parsing/reconstruction

REJECTED: impression_goal as TEXT/VARCHAR
├─ Reason: Always concrete integer, never range
├─ Example: 1500000 (not "1-2000000000")
└─ Impact: Would break fulfillment calculations
```

**Reasoning:**
- Impression goal is ALWAYS a concrete target number for fulfillment calculation
- Runtime parsing must handle "ASAP" as valid start date
- Primary analysis is fulfillment rate: (delivered_impressions / impression_goal) × 100%
- Budget/CPM fields are secondary reference data, not primary analysis focus

**Implications:**
- Database schema optimized for fulfillment calculations
- API design focused on impression delivery metrics
- UI components emphasize delivery vs goal comparisons
- Query patterns optimize for fulfillment percentage calculations

**Runtime Field Parsing Logic:**
```sql
-- Extract start/end dates from runtime field
CASE
  WHEN runtime LIKE 'ASAP-%' THEN
    SPLIT_PART(runtime, '-', 2)::DATE as end_date
  ELSE
    SPLIT_PART(runtime, '-', 1)::DATE as start_date,
    SPLIT_PART(runtime, '-', 2)::DATE as end_date
END
```

---

## Implementation Notes

### Database Optimization Requirements:
- Indexes on: campaign_id, purchase_type, end_date, fulfillment_percentage
- Materialized views for common aggregations may be added later
- Query optimization for real-time aggregation performance

### Frontend Architecture Requirements:
- State management for filter persistence across navigation
- Component lazy loading for large datasets
- Responsive design for executive presentation contexts
- Accessibility compliance for professional use

### API Design Requirements:
- RESTful endpoints supporting flexible query parameters
- Pagination for large result sets
- Caching headers for performance optimization
- Error handling for data quality issues

---

## Future Decision Points

*Areas requiring decisions as development progresses:*

1. **Performance Optimization:** When to add caching/pre-computation if real-time aggregation becomes slow
2. **Advanced Analytics:** What statistical analysis tools to add based on pattern discoveries
3. **Export Capabilities:** What reporting formats stakeholders will need
4. **Alert System:** Whether to add automated underperformance detection
5. **Data Validation:** How to handle incomplete or inconsistent campaign data

---

## Decision Change Log

*Track when and why architectural decisions are modified*

| Date | Decision | Change | Reasoning |
|------|----------|--------|-----------|
| 2025-09-17 | Initial Architecture | All decisions above | Based on PRD analysis and user requirements discussion |

---

*This document should be updated whenever significant architectural decisions are made or changed during development.*