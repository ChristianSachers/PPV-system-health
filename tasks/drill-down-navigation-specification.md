# PPV System Health Monitor - Drill-Down Navigation Specification

*Investigation-focused navigation for system health triage and forensic analysis*
*Last Updated: 2025-09-17*

## Overview

This document defines the navigation system for PPV System Health Monitor, designed around impression delivery fulfillment investigation workflow: system health assessment → impression delivery gap identification → fulfillment shortfall analysis → forensic root cause investigation.

**CRITICAL FOCUS:** All navigation levels optimize for IMPRESSION DELIVERY FULFILLMENT analysis (delivered_impressions / impression_goal), NOT budget/CPM analysis.

**Core Business Questions:**
1. **Level 1:** Are campaigns/deals achieving their impression delivery goals (delivered ≥ impression_goal)?
2. **Level 2:** How do different categories (guaranteed campaigns, unguaranteed campaigns, guaranteed deals) perform against their impression goals?
3. **Level 3:** Which specific campaigns/deals have impression delivery shortfalls requiring investigation?
4. **Level 4:** What exactly caused this impression delivery shortfall and when did it occur?

---

## DNV-001: Investigation Workflow Architecture

**Navigation Philosophy:** Problem identification and forensic analysis workflow

```
Level 1: System Health Triage
    ↓ (Filter by category for detailed analysis)
Level 2: Category-Specific Health Analysis
    ↓ (Focus on underperforming campaigns/deals)
Level 3: Problem-Focused Investigation (Hide fulfilled, show only underperforming)
    ↓ (Forensic analysis of specific problem)
Level 4: Granular Root Cause Analysis (Date/hour picker for precise investigation)
```

**User Mental Model:**
- **Level 1:** "Do I have impression delivery fulfillment problems?"
- **Level 2:** "Where are the category-specific impression shortfalls?"
- **Level 3:** "Which specific campaigns/deals have impression delivery gaps needing my attention?"
- **Level 4:** "What exactly caused this impression delivery shortfall?"

**Data Complexity Progression:**
```
Level 1: ~300 campaigns/deals → 3 summary statistics + time filters (7d/30d/this_year)
Level 2: ~100 campaigns/deals → Category performance + distribution + trends + time filters
Level 3: ~20-50 underperforming → Individual campaign details + daily granularity + site breakdown
Level 4: 1 campaign/deal → Hourly granularity + custom date/hour picker + site breakdown
```

---

## DNV-002: Fulfillment Business Logic

**CORRECTED Fulfillment Definition:**
```sql
-- Impression Delivery Fulfillment calculation (CORRECTED for INTEGER impression_goal)
(c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) as impression_shortfall

-- Fulfillment Percentage (Primary Metric)
CASE
  WHEN c.impression_goal > 0 THEN
    (COALESCE(SUM(r.total_impressions), 0)::FLOAT / c.impression_goal * 100)
  ELSE 0
END as fulfillment_percentage

-- Classification
CASE
  WHEN (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) <= 0 THEN 'goal_met'    -- Delivered >= goal
  WHEN (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) > 0 THEN 'shortfall'    -- Shortfall exists
END as delivery_status
```

**Impression Delivery Categories (Based on fulfillment percentage):**
- **🟢 Goal Met/Exceeded:** `fulfillment_percentage >= 100` (delivered ≥ impression_goal)
- **🟡 Near Goal:** `fulfillment_percentage >= 99.5 AND fulfillment_percentage < 100` (99.5-99.9%)
- **🟠 Moderate Shortfall:** `fulfillment_percentage >= 95 AND fulfillment_percentage < 99.5` (95-99.5%)
- **🔴 Critical Shortfall:** `fulfillment_percentage < 95` (significant impression underdelivery)

**Level 3 Filtering Logic (CORRECTED):**
```sql
-- Show only campaigns/deals with impression delivery shortfalls
WHERE (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) > 0
ORDER BY (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) DESC  -- Worst impression shortfalls first
```

---

## DNV-003: Level 1 - System Health Triage

### Visual Layout:
```
┌─────────────────────────────────────────────────────────────┐
│ PPV SYSTEM HEALTH TRIAGE                                    │
├─────────────────────────────────────────────────────────────┤
│ Time Period: [7 days] [30 days] [This Year]                │
├─────────────────────────────────────────────────────────────┤
│ SYSTEM HEALTH STATUS:                                       │
│ • Total Active: 287 campaigns/deals                        │
│ • Fulfilled: 264 (92.0%) 🟢                               │
│ • Underperforming: 23 (8.0%) 🔴                           │
│                                                             │
│ CATEGORY BREAKDOWN:                                         │
│ ┌─────────────────┬─────────────────┬─────────────────────┐ │
│ │ Guaranteed      │ Unguaranteed    │ Unknown             │ │
│ │ Campaigns       │ Campaigns       │ Purchase Type       │ │
│ │ 145/153 (94.8%) │ 89/117 (76.1%)  │ 0/14 (0%) 🔴      │ │
│ │ [INVESTIGATE]   │ [INVESTIGATE]   │ [INVESTIGATE]       │ │
│ └─────────────────┴─────────────────┴─────────────────────┘ │
│ ┌─────────────────┬─────────────────┬─────────────────────┐ │
│ │ Guaranteed      │ Unguaranteed    │ Unknown             │ │
│ │ Deals          │ Deals           │ Purchase Type       │ │
│ │ 28/30 (93.3%)   │ 2/3 (66.7%) 🟠  │ 0/0 (N/A)          │ │
│ │ [INVESTIGATE]   │ [INVESTIGATE]   │ [INVESTIGATE]       │ │
│ └─────────────────┴─────────────────┴─────────────────────┘ │
│                                                             │
│ KEY INSIGHT: 23 campaigns/deals require immediate attention │
└─────────────────────────────────────────────────────────────┘
```

### Primary Business Questions Answered:
1. **"Are guaranteed campaigns/deals fulfilling ≥100%?"** → 173/183 (94.5%) are fulfilled
2. **"Which need investigation?"** → Click [INVESTIGATE] on categories with problems

### Interaction Specifications:

**Time Filter Actions:**
```javascript
const handleTimeFilterChange = (period) => {
  // Reload all data for selected time period
  const timeRange = {
    '7days': { days: 7, label: 'Last 7 Days' },
    '30days': { days: 30, label: 'Last 30 Days' },
    'this_year': { startDate: '2025-01-01', label: 'This Year' }
  };

  refreshSystemHealth(timeRange[period]);
};
```

**Category Investigation Actions:**
```javascript
const handleCategoryInvestigate = (entityType, purchaseType) => {
  // Navigate to Level 2 with category filter
  navigateToLevel2({
    entityType: entityType,     // 'campaign' or 'deal'
    purchaseType: purchaseType, // 'guaranteed', 'unguaranteed', 'unknown'
    timeWindow: currentTimeWindow,
    focusOn: 'underperforming'  // Hint for Level 2 emphasis
  });
};
```

**Data Requirements:**
```sql
-- Level 1 System Health Query
WITH campaign_fulfillment AS (
  SELECT
    c.campaign_id,
    CASE
      WHEN c.buyer = 'Not set' THEN 'campaign'
      ELSE 'deal'
    END as entity_type,

    COALESCE(r.campaign_purchase_type, r.deal_purchase_type, 'unknown') as purchase_type,

    c.impression_goal,
    COALESCE(SUM(r.total_impressions), 0) as delivered_impressions,
    (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) as shortfall,

    CASE
      WHEN (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) <= 0 THEN 'fulfilled'
      ELSE 'underperforming'
    END as fulfillment_status

  FROM campaigns c
  LEFT JOIN reporting_data r ON (c.campaign_id = r.campaign_id OR c.campaign_id = r.deal_id)
  WHERE c.end_date < NOW()
    AND c.buyer IS NOT NULL
    AND c.end_date >= $time_filter_start
  GROUP BY c.campaign_id, c.impression_goal, c.buyer
)

SELECT
  entity_type,
  purchase_type,
  COUNT(*) as total_count,
  COUNT(CASE WHEN fulfillment_status = 'fulfilled' THEN 1 END) as fulfilled_count,
  COUNT(CASE WHEN fulfillment_status = 'underperforming' THEN 1 END) as underperforming_count,
  ROUND(COUNT(CASE WHEN fulfillment_status = 'fulfilled' THEN 1 END) * 100.0 / COUNT(*), 1) as fulfillment_rate
FROM campaign_fulfillment
GROUP BY entity_type, purchase_type
ORDER BY entity_type, purchase_type;
```

---

## DNV-004: Level 2 - Category-Specific Health Analysis

### Visual Layout:
```
┌─────────────────────────────────────────────────────────────┐
│ GUARANTEED CAMPAIGNS - Health Analysis                     │
├─────────────────────────────────────────────────────────────┤
│ Breadcrumb: [System Health] › Guaranteed Campaigns         │
│ Time Period: [7 days] [30 days] [This Year]                │
├─────────────────────────────────────────────────────────────┤
│ CATEGORY SUMMARY:                                           │
│ • Total: 153 campaigns                                      │
│ • Fulfilled: 145 (94.8%) 🟢                               │
│ • Underperforming: 8 (5.2%) 🔴 ← NEEDS ATTENTION         │
│                                                             │
│ PERFORMANCE DISTRIBUTION:                                   │
│ 🟢 Fulfilled (≥100%):        ████████████████████ 145     │
│ 🟡 Slight Shortfall (98-100%): ██ 3                       │
│ 🟠 Moderate Shortfall (95-98%): █ 2                       │
│ 🔴 Critical Shortfall (<95%):    ██ 3                     │
│                                                             │
│ TREND ANALYSIS:                                             │
│ [Line graph showing fulfillment rate over selected period] │
│ Current: 94.8% | Previous Period: 96.2% | Trend: ↘ -1.4%  │
│                                                             │
│ → [INVESTIGATE UNDERPERFORMING] (Navigate to Level 3)      │
└─────────────────────────────────────────────────────────────┘
```

### Interaction Specifications:

**Focus on Problems Action:**
```javascript
const handleInvestigateUnderperforming = () => {
  // Navigate to Level 3 with underperforming filter pre-applied
  navigateToLevel3({
    entityType: currentEntityType,
    purchaseType: currentPurchaseType,
    timeWindow: currentTimeWindow,
    showOnly: 'underperforming'  // Critical filter for Level 3
  });
};
```

**Trend Analysis:**
```sql
-- Level 2 Trend Analysis Query
WITH period_comparison AS (
  SELECT
    'current' as period,
    COUNT(CASE WHEN fulfillment_status = 'fulfilled' THEN 1 END) * 100.0 / COUNT(*) as fulfillment_rate
  FROM campaign_fulfillment
  WHERE entity_type = $entity_type
    AND purchase_type = $purchase_type
    AND end_date >= $current_period_start

  UNION ALL

  SELECT
    'previous' as period,
    COUNT(CASE WHEN fulfillment_status = 'fulfilled' THEN 1 END) * 100.0 / COUNT(*) as fulfillment_rate
  FROM campaign_fulfillment
  WHERE entity_type = $entity_type
    AND purchase_type = $purchase_type
    AND end_date >= $previous_period_start
    AND end_date < $current_period_start
)

SELECT
  current.fulfillment_rate as current_rate,
  previous.fulfillment_rate as previous_rate,
  (current.fulfillment_rate - previous.fulfillment_rate) as trend_change
FROM period_comparison current
JOIN period_comparison previous ON previous.period = 'previous'
WHERE current.period = 'current';
```

---

## DNV-005: Level 3 - Problem-Focused Investigation

### Visual Layout:
```
┌─────────────────────────────────────────────────────────────┐
│ UNDERPERFORMING GUARANTEED CAMPAIGNS                       │
├─────────────────────────────────────────────────────────────┤
│ Breadcrumb: [System Health] › [Guaranteed Campaigns] › Problems │
│ Filter: Showing ONLY underperforming (fulfilled campaigns hidden) │
├─────────────────────────────────────────────────────────────┤
│ PROBLEM CAMPAIGNS (8 total):                               │
│                                                             │
│ Campaign Name                │ Goal    │ Delivered │ Shortfall │
│ ────────────────────────────────────────────────────────────── │
│ DENTSU_Campaign_X [ANALYZE]  │ 1.2M    │ 750K     │ 450K 🔴  │
│ UML_GIGA_Campaign_Y [ANALYZE]│ 850K    │ 820K     │ 30K 🟡   │
│ Not_Set_Campaign_Z [ANALYZE] │ 2.1M    │ 1.85M    │ 250K 🟠  │
│ Frankfurt_Deal_A [ANALYZE]   │ 500K    │ 485K     │ 15K 🟡   │
│ Berlin_Campaign_B [ANALYZE]  │ 1.5M    │ 1.35M    │ 150K 🟠  │
│                                                             │
│ DAILY PERFORMANCE PATTERN:                                  │
│  100% ┤ ██████████████████████████████████████████████     │
│   75% ┤ ██████████████████████████████████████████████     │
│   50% ┤ ██████████████████▓▓▓▓██████████████████████       │
│   25% ┤ ██████████████████▓▓▓▓██████████████████████       │
│       └─────────────────────────────────────────────────── │
│       Day1  Day5  Day10  Day15  Day20  Day25  Day30        │
│                                                             │
│ KEY INSIGHTS:                                               │
│ • Worst performer: DENTSU_Campaign_X (37.5% shortfall)     │
│ • Performance dip: Days 17-21 across multiple campaigns    │
│ • Site breakdown available for detailed analysis           │
└─────────────────────────────────────────────────────────────┘
```

### Critical Business Logic:

**Hide Fulfilled Campaigns:**
```sql
-- Level 3: Show ONLY underperforming campaigns/deals
SELECT
  c.campaign_id,
  c.campaign_name,
  c.impression_goal,
  COALESCE(SUM(r.total_impressions), 0) as delivered_impressions,
  (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) as shortfall,

  -- Shortfall severity classification
  CASE
    WHEN (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) > (c.impression_goal * 0.05) THEN 'critical'
    WHEN (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) > (c.impression_goal * 0.02) THEN 'moderate'
    ELSE 'slight'
  END as shortfall_severity,

  -- Daily performance breakdown
  ARRAY_AGG(
    JSON_BUILD_OBJECT(
      'date', DATE(r.date_hour),
      'impressions', SUM(r.total_impressions),
      'sites', COUNT(DISTINCT r.site_name)
    ) ORDER BY DATE(r.date_hour)
  ) as daily_breakdown

FROM campaigns c
LEFT JOIN reporting_data r ON (c.campaign_id = r.campaign_id OR c.campaign_id = r.deal_id)
WHERE c.end_date < NOW()
  AND c.buyer IS NOT NULL
  AND entity_type = $entity_type
  AND purchase_type = $purchase_type
  AND (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) > 0  -- ONLY underperforming
GROUP BY c.campaign_id, c.campaign_name, c.impression_goal
ORDER BY shortfall DESC;  -- Worst problems first
```

### Interaction Specifications:

**Campaign Analysis Action:**
```javascript
const handleCampaignAnalyze = (campaignId) => {
  // Navigate to Level 4 for forensic analysis
  navigateToLevel4({
    campaignId: campaignId,
    timeframe: 'full_runtime',  // Default to full campaign runtime
    granularity: 'hourly',      // Level 4 granularity
    analysisType: 'comprehensive'
  });
};
```

---

## DNV-006: Level 4 - Granular Root Cause Analysis

### Visual Layout:
```
┌─────────────────────────────────────────────────────────────┐
│ FORENSIC ANALYSIS: DENTSU_Campaign_X                       │
├─────────────────────────────────────────────────────────────┤
│ Breadcrumb: [System Health] › [Guaranteed Campaigns] › [Problems] › DENTSU_Campaign_X │
├─────────────────────────────────────────────────────────────┤
│ CAMPAIGN DETAILS:                                           │
│ • Runtime: 2025-08-01 to 2025-08-31 (31 days)            │
│ • Goal: 1,200,000 impressions                             │
│ • Delivered: 750,000 impressions (62.5%)                  │
│ • Shortfall: 450,000 impressions 🔴                       │
│                                                             │
│ TIMEFRAME ANALYSIS:                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ From: [2025-08-01 ▼] [00:00 ▼]                        │ │
│ │ To:   [2025-08-31 ▼] [23:59 ▼]                        │ │
│ │ [Apply Custom Range] [Reset to Full Runtime]           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ HOURLY PERFORMANCE PATTERN:                                 │
│  100% ┤ ██  ██  ██      ██  ██  ██  ██  ██               │
│   75% ┤ ██  ██  ██      ██  ██  ██  ██  ██               │
│   50% ┤ ██  ██  ██  ▓▓  ██  ██  ██  ██  ██               │
│   25% ┤ ██  ██  ██  ▓▓  ██  ██  ██  ██  ██               │
│    0% ┤ ──  ──  ──  ──  ──  ──  ──  ──  ──               │
│       00  02  04  06  08  10  12  14  16  18  20  22     │
│                                                             │
│ SITE BREAKDOWN:                                             │
│ Top Underperforming Sites (within selected timeframe):     │
│ • München Hbf: 45% delivery (expected 89,149, got 40,117) │
│ • Berlin Alex: 38% delivery (expected 76,233, got 28,968) │
│ • Hamburg Term: 52% delivery (expected 82,441, got 42,869)│
│                                                             │
│ ROOT CAUSE INSIGHTS:                                        │
│ • Critical Issue: Performance drops 06:00-10:00 daily      │
│ • Affected Period: Entire campaign runtime                 │
│ • Primary Impact: Major sites show 40-52% delivery rates   │
│ • Likely Cause: Insufficient bid requests during early hours│
│                                                             │
│ RECOMMENDATIONS:                                            │
│ • Investigate inventory availability 06:00-10:00           │
│ • Check bid request volume for affected sites              │
│ • Consider campaign optimization for peak hours            │
└─────────────────────────────────────────────────────────────┘
```

### Date/Hour Picker Implementation:

```javascript
const TimeframePicker = ({ campaignRuntime, onTimeframeChange }) => {
  const [fromDate, setFromDate] = useState(campaignRuntime.startDate);
  const [fromHour, setFromHour] = useState('00:00');
  const [toDate, setToDate] = useState(campaignRuntime.endDate);
  const [toHour, setToHour] = useState('23:59');

  const handleApplyCustomRange = () => {
    const customTimeframe = {
      startDateTime: `${fromDate}T${fromHour}:00.000Z`,
      endDateTime: `${toDate}T${toHour}:00.000Z`,
      isCustom: true
    };

    onTimeframeChange(customTimeframe);
  };

  const handleResetToFullRuntime = () => {
    const fullTimeframe = {
      startDateTime: campaignRuntime.startDate,
      endDateTime: campaignRuntime.endDate,
      isCustom: false
    };

    setFromDate(campaignRuntime.startDate.split('T')[0]);
    setFromHour('00:00');
    setToDate(campaignRuntime.endDate.split('T')[0]);
    setToHour('23:59');

    onTimeframeChange(fullTimeframe);
  };

  return (
    <div className="timeframe-picker">
      <div className="date-range">
        <label>From:</label>
        <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)}
               min={campaignRuntime.startDate.split('T')[0]}
               max={campaignRuntime.endDate.split('T')[0]} />
        <input type="time" value={fromHour} onChange={(e) => setFromHour(e.target.value)} />
      </div>

      <div className="date-range">
        <label>To:</label>
        <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)}
               min={fromDate}
               max={campaignRuntime.endDate.split('T')[0]} />
        <input type="time" value={toHour} onChange={(e) => setToHour(e.target.value)} />
      </div>

      <div className="actions">
        <button onClick={handleApplyCustomRange}>Apply Custom Range</button>
        <button onClick={handleResetToFullRuntime}>Reset to Full Runtime</button>
      </div>
    </div>
  );
};
```

### Forensic Analysis Query:

```sql
-- Level 4: Hourly granularity within custom timeframe
WITH hourly_performance AS (
  SELECT
    r.site_name,
    DATE_TRUNC('hour', r.date_hour) as hour_timestamp,
    SUM(r.total_impressions) as hourly_impressions,
    SUM(r.bids) as hourly_bids,
    SUM(r.auction_wins) as hourly_wins,

    -- Calculate hourly performance rate
    CASE
      WHEN SUM(r.bids) > 0 THEN
        (SUM(r.auction_wins)::FLOAT / SUM(r.bids) * 100)
      ELSE 0
    END as hourly_win_rate

  FROM reporting_data r
  WHERE (r.campaign_id = $campaign_id OR r.deal_id = $campaign_id)
    AND r.date_hour >= $custom_start_datetime
    AND r.date_hour <= $custom_end_datetime
  GROUP BY r.site_name, DATE_TRUNC('hour', r.date_hour)
),

site_summary AS (
  SELECT
    site_name,
    SUM(hourly_impressions) as total_site_impressions,
    AVG(hourly_win_rate) as avg_site_win_rate,
    COUNT(*) as active_hours,

    -- Identify problematic hours
    COUNT(CASE WHEN hourly_win_rate < 50 THEN 1 END) as problematic_hours

  FROM hourly_performance
  GROUP BY site_name
)

-- Return both hourly patterns and site summaries
SELECT
  'hourly' as data_type,
  JSON_AGG(
    JSON_BUILD_OBJECT(
      'hour', EXTRACT(HOUR FROM hour_timestamp),
      'impressions', hourly_impressions,
      'win_rate', hourly_win_rate,
      'site', site_name
    ) ORDER BY hour_timestamp
  ) as hourly_data
FROM hourly_performance

UNION ALL

SELECT
  'site_summary' as data_type,
  JSON_AGG(
    JSON_BUILD_OBJECT(
      'site', site_name,
      'total_impressions', total_site_impressions,
      'avg_win_rate', avg_site_win_rate,
      'problematic_hours', problematic_hours
    ) ORDER BY total_site_impressions DESC
  ) as site_data
FROM site_summary;
```

---

## DNV-007: Navigation State Management

### Investigation Context Preservation:
```javascript
const InvestigationContext = {
  systemHealth: {
    timeWindow: '30days',
    lastRefresh: '2025-09-17T10:30:00Z'
  },
  categoryAnalysis: {
    entityType: 'campaign',
    purchaseType: 'guaranteed',
    timeWindow: '30days',
    focusArea: 'underperforming'
  },
  problemInvestigation: {
    filters: { showOnly: 'underperforming' },
    sortBy: 'shortfall_desc',
    selectedCampaigns: []
  },
  forensicAnalysis: {
    campaignId: 'abc-123',
    customTimeframe: {
      start: '2025-08-01T00:00:00Z',
      end: '2025-08-31T23:59:59Z',
      isCustom: false
    },
    analysisType: 'comprehensive'
  }
};
```

### Breadcrumb Navigation:
```javascript
const InvestigationBreadcrumb = ({ currentLevel, context }) => {
  const breadcrumbMap = {
    1: { label: 'System Health', path: '/health-triage' },
    2: {
      label: `${context.categoryAnalysis?.entityType} - ${context.categoryAnalysis?.purchaseType}`,
      path: `/category-analysis/${context.categoryAnalysis?.entityType}/${context.categoryAnalysis?.purchaseType}`
    },
    3: {
      label: 'Problem Investigation',
      path: `/problems/${context.categoryAnalysis?.entityType}/${context.categoryAnalysis?.purchaseType}`
    },
    4: {
      label: context.forensicAnalysis?.campaignName || 'Forensic Analysis',
      path: `/forensic/${context.forensicAnalysis?.campaignId}`
    }
  };

  return (
    <nav className="investigation-breadcrumb">
      {Array.from({ length: currentLevel }, (_, i) => i + 1).map(level => (
        <BreadcrumbItem
          key={level}
          level={level}
          {...breadcrumbMap[level]}
          isActive={level === currentLevel}
          onClick={() => navigateToLevel(level, context)}
        />
      ))}
    </nav>
  );
};
```

---

## DNV-008: Implementation Architecture

### Investigation Flow Controller:

```javascript
class InvestigationFlowController {
  constructor(dataService, navigationService) {
    this.data = dataService;
    this.navigation = navigationService;
  }

  // Level 1: System health assessment
  async loadSystemHealthTriage(timeWindow = '30days') {
    const healthData = await this.data.getSystemHealthSummary(timeWindow);

    return {
      systemStatus: this.assessSystemHealth(healthData),
      categoryBreakdown: this.categorizeCampaignHealth(healthData),
      actionRequired: this.identifyActionItems(healthData),
      timeWindow: timeWindow
    };
  }

  // Level 2: Category-specific analysis
  async loadCategoryAnalysis(entityType, purchaseType, timeWindow) {
    const [categoryData, trendData] = await Promise.all([
      this.data.getCategoryPerformance(entityType, purchaseType, timeWindow),
      this.data.getCategoryTrends(entityType, purchaseType, timeWindow)
    ]);

    return {
      categoryHealth: categoryData,
      performanceDistribution: this.analyzeDistribution(categoryData),
      trends: trendData,
      underperformingCount: categoryData.filter(c => c.shortfall > 0).length
    };
  }

  // Level 3: Problem-focused investigation (hide fulfilled)
  async loadProblemInvestigation(entityType, purchaseType, timeWindow) {
    const underperformingOnly = await this.data.getUnderperformingCampaigns(
      entityType,
      purchaseType,
      timeWindow
    );

    return {
      problemCampaigns: underperformingOnly,
      severityAnalysis: this.analyzeProblemSeverity(underperformingOnly),
      dailyPatterns: this.identifyDailyPatterns(underperformingOnly),
      recommendations: this.generateInvestigationSuggestions(underperformingOnly)
    };
  }

  // Level 4: Forensic root cause analysis
  async loadForensicAnalysis(campaignId, customTimeframe = null) {
    const campaign = await this.data.getCampaignDetails(campaignId);
    const timeframe = customTimeframe || {
      start: campaign.startDate,
      end: campaign.endDate
    };

    const [hourlyData, siteBreakdown] = await Promise.all([
      this.data.getHourlyPerformance(campaignId, timeframe),
      this.data.getSiteBreakdown(campaignId, timeframe)
    ]);

    return {
      campaignDetails: campaign,
      timeframeAnalysis: timeframe,
      hourlyPatterns: this.analyzeHourlyPatterns(hourlyData),
      sitePerformance: siteBreakdown,
      rootCauseInsights: this.generateRootCauseAnalysis(hourlyData, siteBreakdown),
      recommendations: this.generateForensicRecommendations(hourlyData, siteBreakdown)
    };
  }

  // Helper: Assess overall system health
  assessSystemHealth(data) {
    const totalCampaigns = data.reduce((sum, item) => sum + item.total_count, 0);
    const fulfilledCampaigns = data.reduce((sum, item) => sum + item.fulfilled_count, 0);
    const fulfillmentRate = (fulfilledCampaigns / totalCampaigns) * 100;

    return {
      status: fulfillmentRate >= 95 ? 'healthy' : fulfillmentRate >= 90 ? 'warning' : 'critical',
      fulfillmentRate: fulfillmentRate,
      totalCampaigns: totalCampaigns,
      problemCount: totalCampaigns - fulfilledCampaigns
    };
  }

  // Helper: Generate root cause analysis
  generateRootCauseAnalysis(hourlyData, siteData) {
    const insights = [];

    // Identify time-based patterns
    const problematicHours = hourlyData.filter(h => h.win_rate < 50);
    if (problematicHours.length > 0) {
      insights.push({
        type: 'temporal_pattern',
        description: `Performance drops during hours: ${problematicHours.map(h => h.hour).join(', ')}`,
        impact: 'high',
        recommendation: 'Investigate inventory availability during identified hours'
      });
    }

    // Identify site-based patterns
    const underperformingSites = siteData.filter(s => s.avg_win_rate < 60);
    if (underperformingSites.length > 0) {
      insights.push({
        type: 'site_pattern',
        description: `${underperformingSites.length} sites significantly underperforming`,
        impact: 'high',
        recommendation: 'Check bid request volume and inventory quality for affected sites'
      });
    }

    return insights;
  }
}
```

---

## DNV-009: CRITICAL Database Schema Navigation Corrections

**MANDATORY CORRECTIONS:** Fix navigation queries for correct data structure

**CORRECTED Campaign Schema for Navigation:**
```sql
-- Navigation queries must use CORRECTED schema
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    impression_goal INTEGER NOT NULL,  -- CORRECTED: INTEGER not range string
    runtime TEXT NOT NULL,             -- CORRECTED: Single field not separate dates
    buyer TEXT
);
```

**Level 1 System Health Query (CORRECTED):**
```sql
WITH campaign_fulfillment AS (
  SELECT
    c.campaign_id,
    c.impression_goal,  -- INTEGER field
    c.runtime,          -- TEXT field to parse

    -- Parse runtime for end date filtering
    CASE
      WHEN c.runtime LIKE 'ASAP-%' THEN
        TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
      ELSE
        TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
    END as campaign_end_date,

    -- Entity classification
    CASE
      WHEN c.buyer = 'Not set' THEN 'campaign'
      ELSE 'deal'
    END as entity_type,

    -- Purchase type from reporting data
    COALESCE(r.campaign_purchase_type, r.deal_purchase_type, 'unknown') as purchase_type,

    -- Core fulfillment metrics
    COALESCE(SUM(r.total_impressions), 0) as delivered_impressions,
    (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) as impression_shortfall,

    CASE
      WHEN c.impression_goal > 0 THEN
        (COALESCE(SUM(r.total_impressions), 0)::FLOAT / c.impression_goal * 100)
      ELSE 0
    END as fulfillment_percentage,

    CASE
      WHEN (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) <= 0 THEN 'goal_met'
      ELSE 'shortfall'
    END as delivery_status

  FROM campaigns c
  LEFT JOIN reporting_data r ON (c.campaign_id = r.campaign_id OR c.campaign_id = r.deal_id)
  WHERE
    -- Filter completed campaigns using parsed runtime
    CASE
      WHEN c.runtime LIKE 'ASAP-%' THEN
        TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
      ELSE
        TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
    END < CURRENT_DATE
    AND c.buyer IS NOT NULL
  GROUP BY c.campaign_id, c.impression_goal, c.runtime, c.buyer
)

-- System health summary for Level 1 navigation
SELECT
  entity_type,
  purchase_type,
  COUNT(*) as total_count,
  COUNT(CASE WHEN delivery_status = 'goal_met' THEN 1 END) as goal_met_count,
  COUNT(CASE WHEN delivery_status = 'shortfall' THEN 1 END) as shortfall_count,
  ROUND(COUNT(CASE WHEN delivery_status = 'goal_met' THEN 1 END) * 100.0 / COUNT(*), 1) as fulfillment_rate
FROM campaign_fulfillment
GROUP BY entity_type, purchase_type
ORDER BY entity_type, purchase_type;
```

**Level 3 Problem Investigation Query (CORRECTED):**
```sql
-- Show ONLY campaigns/deals with impression delivery shortfalls
SELECT
  c.campaign_id,
  c.campaign_name,
  c.impression_goal,  -- INTEGER field
  c.runtime,          -- TEXT field

  -- Parse runtime for display
  CASE
    WHEN c.runtime LIKE 'ASAP-%' THEN
      'ASAP - ' || SPLIT_PART(c.runtime, '-', 2)
    ELSE
      REPLACE(c.runtime, '-', ' to ')
  END as runtime_display,

  COALESCE(SUM(r.total_impressions), 0) as delivered_impressions,
  (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) as impression_shortfall,

  CASE
    WHEN c.impression_goal > 0 THEN
      (COALESCE(SUM(r.total_impressions), 0)::FLOAT / c.impression_goal * 100)
    ELSE 0
  END as fulfillment_percentage,

  -- Shortfall severity classification
  CASE
    WHEN (COALESCE(SUM(r.total_impressions), 0)::FLOAT / c.impression_goal * 100) >= 99.5 THEN 'moderate'
    WHEN (COALESCE(SUM(r.total_impressions), 0)::FLOAT / c.impression_goal * 100) >= 95 THEN 'significant'
    ELSE 'critical'
  END as shortfall_severity

FROM campaigns c
LEFT JOIN reporting_data r ON (c.campaign_id = r.campaign_id OR c.campaign_id = r.deal_id)
WHERE
  -- Only completed campaigns with shortfalls
  CASE
    WHEN c.runtime LIKE 'ASAP-%' THEN
      TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
    ELSE
      TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
  END < CURRENT_DATE
  AND c.buyer IS NOT NULL
  AND entity_type = $entity_type
  AND purchase_type = $purchase_type
GROUP BY c.campaign_id, c.campaign_name, c.impression_goal, c.runtime, c.buyer
HAVING (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) > 0  -- ONLY shortfalls
ORDER BY impression_shortfall DESC;  -- Worst shortfalls first
```

---

## DNV-010: Implementation Checklist

### Core Navigation Components:
- [ ] Level1SystemHealthTriage with time filters and category breakdown
- [ ] Level2CategoryAnalysis with trend analysis and underperforming focus
- [ ] Level3ProblemInvestigation with fulfilled campaigns hidden
- [ ] Level4ForensicAnalysis with date/hour picker and root cause insights

### Investigation Workflow:
- [ ] System health assessment with fulfillment calculation
- [ ] Category filtering with entity type and purchase type
- [ ] Problem identification with shortfall-based sorting
- [ ] Forensic analysis with custom timeframe selection

### Data Management:
- [ ] Fulfillment calculation: (goal - delivered) for shortfall identification
- [ ] Time window presets: 7days, 30days, this_year
- [ ] Custom date/hour picker within campaign runtime
- [ ] Performance categorization based on shortfall severity

### User Experience:
- [ ] Investigation-focused breadcrumb navigation
- [ ] Context preservation across navigation levels
- [ ] Root cause insight generation
- [ ] Actionable recommendations at each level

---

*This navigation specification enables systematic investigation from system health assessment to granular forensic analysis, supporting the product manager's workflow for identifying and resolving campaign fulfillment issues.*