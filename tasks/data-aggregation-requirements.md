# PPV System Health Monitor - Data Aggregation Requirements

*Comprehensive specification for data processing, classification, and aggregation patterns*
*Last Updated: 2025-09-17*

## Overview

This document defines the data aggregation requirements for the PPV System Health Monitor, specifying how raw campaign and reporting data transforms into impression delivery fulfillment insights. Each requirement includes fulfillment business logic, SQL patterns, performance considerations, and API specifications.

**CRITICAL FOCUS:** All aggregation patterns optimize for FULFILLMENT ANALYSIS (delivered_impressions / impression_goal), NOT budget/CPM analysis.

---

## DAR-001: Entity Classification Logic

**Business Rules:**
- **Campaign:** `buyer = 'Not set'`
- **Deal:** `buyer != 'Not set'` AND `buyer IS NOT NULL`
- **Data Quality Issue:** `buyer IS NULL` (excluded from analysis, reported during upload)

**Implementation:**
```sql
-- Entity Type Classification
CASE
  WHEN c.buyer = 'Not set' THEN 'campaign'
  WHEN c.buyer IS NOT NULL THEN 'deal'
  -- buyer IS NULL excluded from analysis queries
END as entity_type
```

**Data Quality Handling:**
- **During Upload:** Report count of excluded records with reason
- **During Analysis:** Filter out `buyer IS NULL` records entirely
- **Upload Feedback:** "X campaigns excluded due to missing buyer information"

**Validation Query:**
```sql
-- Upload data quality check
SELECT
  COUNT(*) as total_records,
  COUNT(CASE WHEN buyer IS NOT NULL THEN 1 END) as valid_records,
  COUNT(CASE WHEN buyer IS NULL THEN 1 END) as excluded_records
FROM campaigns_upload;
```

---

## DAR-002: Purchase Type Classification

**Business Rules:**
- **Source:** Purchase type comes from reporting data, NOT campaign XLSX
- **Campaign Purchase Type:** From `reporting_data.campaign_purchase_type`
- **Deal Purchase Type:** From `reporting_data.deal_purchase_type`
- **Unknown Category:** When campaign exists but has no reporting data

**Implementation:**
```sql
-- Purchase Type from Reporting Data
COALESCE(
  r.campaign_purchase_type,  -- For campaigns
  r.deal_purchase_type,      -- For deals
  'unknown'                  -- For missing reporting data
) as purchase_type
```

**Filter Categories:**
1. `guaranteed` - High priority fulfillment expectations
2. `unguaranteed` - Lower priority, best-effort fulfillment
3. `unknown` - Campaigns/deals without reporting data (0% performance)

---

## DAR-003: Impression Delivery Fulfillment Calculation Pattern

**CRITICAL CORRECTION:** impression_goal is INTEGER field, NOT range string

**Core Business Logic:**
```sql
-- Fulfillment Percentage Calculation (CORRECTED)
CASE
  WHEN c.impression_goal > 0 THEN
    (COALESCE(SUM(r.total_impressions), 0)::FLOAT / c.impression_goal * 100)
  ELSE 0
END as fulfillment_percentage

-- Shortfall Calculation (Primary Metric)
(c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) as impression_shortfall
```

**Fulfillment Classification (Impression Delivery Focus):**
- **🟢 Goal Met/Exceeded:** `≥ 100%` (delivered ≥ impression_goal)
- **🟡 Near Goal:** `99.5% - 99.9%` (slight impression shortfall)
- **🟠 Moderate Shortfall:** `95% - 99.5%` (moderate impression gap)
- **🔴 Critical Shortfall:** `< 95%` (significant impression underdelivery)

**Implementation:**
```sql
-- Fulfillment Category Classification (CORRECTED)
CASE
  WHEN fulfillment_percentage >= 100 THEN 'goal_met'
  WHEN fulfillment_percentage >= 99.5 THEN 'near_goal'
  WHEN fulfillment_percentage >= 95 THEN 'moderate_shortfall'
  ELSE 'critical_shortfall'
END as fulfillment_category

-- Primary Business Metric: Impression Shortfall
CASE
  WHEN (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) <= 0 THEN 'fulfilled'
  ELSE 'underperforming'
END as delivery_status
```

---

## DAR-004: Primary Visualization - Fulfillment Gap Analysis

**Query Pattern:**
```sql
WITH campaign_performance AS (
  SELECT
    c.campaign_id,
    c.campaign_name,
    c.impression_goal,
    c.start_date,
    c.end_date,

    -- Entity classification
    CASE
      WHEN c.buyer = 'Not set' THEN 'campaign'
      ELSE 'deal'
    END as entity_type,

    -- Purchase type from reporting data
    COALESCE(
      r.campaign_purchase_type,
      r.deal_purchase_type,
      'unknown'
    ) as purchase_type,

    -- Aggregated performance metrics
    COALESCE(SUM(r.total_impressions), 0) as delivered_impressions,
    COALESCE(SUM(r.bids), 0) as total_bids,
    COALESCE(SUM(r.auction_wins), 0) as total_wins,

    -- Fulfillment calculation
    CASE
      WHEN c.impression_goal > 0 THEN
        (COALESCE(SUM(r.total_impressions), 0) / c.impression_goal * 100)
      ELSE 0
    END as fulfillment_percentage,

    -- Performance categorization
    CASE
      WHEN (COALESCE(SUM(r.total_impressions), 0) / c.impression_goal * 100) > 100 THEN 'excellent'
      WHEN (COALESCE(SUM(r.total_impressions), 0) / c.impression_goal * 100) >= 99.5 THEN 'good'
      WHEN (COALESCE(SUM(r.total_impressions), 0) / c.impression_goal * 100) >= 98 THEN 'warning'
      ELSE 'critical'
    END as performance_category

  FROM campaigns c
  LEFT JOIN reporting_data r ON (
    c.campaign_id = r.campaign_id OR
    c.campaign_id = r.deal_id
  )
  WHERE c.end_date < NOW()  -- Only completed campaigns
    AND c.buyer IS NOT NULL -- Exclude data quality issues
  GROUP BY c.campaign_id, c.campaign_name, c.impression_goal, c.buyer, c.start_date, c.end_date
)

SELECT * FROM campaign_performance
WHERE 1=1
  AND ($purchase_type_filter IS NULL OR purchase_type = $purchase_type_filter)
  AND ($performance_threshold IS NULL OR fulfillment_percentage < $performance_threshold)
  AND ($time_window IS NULL OR end_date >= NOW() - INTERVAL $time_window DAY)
ORDER BY fulfillment_percentage ASC;
```

**API Response Structure:**
```json
{
  "campaigns": [
    {
      "campaignId": "abc-123",
      "campaignName": "DENTSU_AEGIS_Campaign_X",
      "entityType": "campaign",
      "purchaseType": "guaranteed",
      "impressionGoal": 1200000,
      "deliveredImpressions": 1128400,
      "fulfillmentPercentage": 94.2,
      "performanceCategory": "warning",
      "totalBids": 15420,
      "totalWins": 8934,
      "startDate": "2025-08-01T00:00:00.000Z",
      "endDate": "2025-08-31T23:59:59.000Z"
    }
  ],
  "summary": {
    "totalCampaigns": 287,
    "averageFulfillment": 94.2,
    "performanceDistribution": {
      "excellent": 45,
      "good": 38,
      "warning": 21,
      "critical": 7
    }
  }
}
```

---

## DAR-005: Secondary Visualization - Temporal Trend Analysis

**Rolling Window Pattern:**
```sql
WITH daily_performance AS (
  SELECT
    DATE(r.date_hour) as performance_date,

    -- Purchase type classification
    COALESCE(
      r.campaign_purchase_type,
      r.deal_purchase_type,
      'unknown'
    ) as purchase_type,

    -- Daily aggregations
    COUNT(DISTINCT c.campaign_id) as active_campaigns,
    SUM(r.total_impressions) as daily_impressions,
    SUM(c.impression_goal) as daily_goals,

    -- Daily fulfillment rate
    CASE
      WHEN SUM(c.impression_goal) > 0 THEN
        (SUM(r.total_impressions) / SUM(c.impression_goal) * 100)
      ELSE 0
    END as daily_fulfillment_rate

  FROM campaigns c
  JOIN reporting_data r ON (
    c.campaign_id = r.campaign_id OR
    c.campaign_id = r.deal_id
  )
  WHERE r.date_hour >= NOW() - INTERVAL $time_window DAY
    AND c.end_date < NOW()
    AND c.buyer IS NOT NULL
  GROUP BY DATE(r.date_hour), purchase_type
),

rolling_windows AS (
  SELECT
    performance_date,
    purchase_type,
    active_campaigns,
    daily_impressions,
    daily_fulfillment_rate,

    -- 7-day rolling average
    AVG(daily_fulfillment_rate) OVER (
      PARTITION BY purchase_type
      ORDER BY performance_date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_7day_fulfillment,

    -- Trend calculation (vs 7 days ago)
    daily_fulfillment_rate - LAG(daily_fulfillment_rate, 7) OVER (
      PARTITION BY purchase_type
      ORDER BY performance_date
    ) as trend_change_7day

  FROM daily_performance
)

SELECT * FROM rolling_windows
WHERE performance_date >= NOW() - INTERVAL $time_window DAY
ORDER BY performance_date DESC, purchase_type;
```

**Trend Classification:**
- **↗ Improving:** `trend_change_7day > 1.0`
- **↘ Declining:** `trend_change_7day < -1.0`
- **→ Stable:** `-1.0 <= trend_change_7day <= 1.0`

---

## DAR-006: Drill-Down Level Data Requirements

### Level 2: Campaign Category Analysis
```sql
-- Performance distribution within purchase type
SELECT
  performance_category,
  COUNT(*) as campaign_count,
  AVG(fulfillment_percentage) as avg_fulfillment,
  STRING_AGG(
    campaign_name || ' (' || ROUND(fulfillment_percentage, 1) || '%)',
    ', ' ORDER BY fulfillment_percentage ASC
  ) as worst_performers
FROM campaign_performance  -- From DAR-004 CTE
WHERE purchase_type = $selected_purchase_type
GROUP BY performance_category
ORDER BY
  CASE performance_category
    WHEN 'critical' THEN 1
    WHEN 'warning' THEN 2
    WHEN 'good' THEN 3
    WHEN 'excellent' THEN 4
  END;
```

### Level 3: Individual Campaign Analysis
```sql
-- Single campaign detailed performance
SELECT
  c.*,
  -- Temporal breakdown by day
  DATE(r.date_hour) as day,
  SUM(r.total_impressions) as daily_impressions,
  SUM(r.bids) as daily_bids,
  SUM(r.auction_wins) as daily_wins,
  COUNT(DISTINCT r.site_name) as active_sites
FROM campaign_performance c
JOIN reporting_data r ON (c.campaign_id = r.campaign_id OR c.campaign_id = r.deal_id)
WHERE c.campaign_id = $selected_campaign_id
GROUP BY c.campaign_id, DATE(r.date_hour)
ORDER BY day;
```

### Level 4: Site/Time Forensic Analysis
```sql
-- Hourly site-level performance
SELECT
  r.site_name,
  EXTRACT(HOUR FROM r.date_hour) as hour,
  DATE(r.date_hour) as day,
  SUM(r.total_impressions) as hourly_impressions,
  SUM(r.bids) as hourly_bids,
  SUM(r.auction_wins) as hourly_wins,
  -- Performance ratio
  CASE
    WHEN SUM(r.bids) > 0 THEN
      (SUM(r.auction_wins)::FLOAT / SUM(r.bids) * 100)
    ELSE 0
  END as win_rate_percentage
FROM reporting_data r
WHERE (r.campaign_id = $selected_campaign_id OR r.deal_id = $selected_campaign_id)
  AND r.date_hour >= $analysis_start_date
  AND r.date_hour <= $analysis_end_date
GROUP BY r.site_name, EXTRACT(HOUR FROM r.date_hour), DATE(r.date_hour)
ORDER BY site_name, day, hour;
```

---

## DAR-007: Performance Optimization Requirements

### Database Indexes:
```sql
-- Primary performance indexes
CREATE INDEX idx_campaigns_analysis ON campaigns(end_date, buyer)
  WHERE end_date < NOW() AND buyer IS NOT NULL;

CREATE INDEX idx_campaigns_buyer_type ON campaigns(buyer);

CREATE INDEX idx_reporting_campaign_lookup ON reporting_data(campaign_id, date_hour)
  INCLUDE (total_impressions, bids, auction_wins);

CREATE INDEX idx_reporting_deal_lookup ON reporting_data(deal_id, date_hour)
  INCLUDE (total_impressions, bids, auction_wins);

CREATE INDEX idx_reporting_purchase_types ON reporting_data(campaign_purchase_type, deal_purchase_type);

-- Temporal analysis optimization
CREATE INDEX idx_reporting_temporal ON reporting_data(date_hour, campaign_id, deal_id)
  INCLUDE (total_impressions);

-- Site analysis optimization
CREATE INDEX idx_reporting_site_analysis ON reporting_data(campaign_id, deal_id, site_name, date_hour);
```

### Caching Strategy:
```javascript
// Cache configuration for aggregation service
const CACHE_CONFIG = {
  fulfillmentGaps: {
    ttl: 300,  // 5 minutes - balance real-time feel with performance
    keyPattern: 'fulfillment_{purchaseType}_{threshold}_{timeWindow}'
  },
  temporalTrends: {
    ttl: 600,  // 10 minutes - less frequent changes
    keyPattern: 'temporal_{purchaseType}_{timeWindow}'
  },
  campaignDetails: {
    ttl: 900,  // 15 minutes - individual campaign data changes less
    keyPattern: 'campaign_{campaignId}_{analysisType}'
  }
};
```

---

## DAR-008: Data Quality Validation Requirements

### Upload Validation:
```sql
-- Data quality report during XLSX upload
WITH upload_quality AS (
  SELECT
    COUNT(*) as total_uploads,
    COUNT(CASE WHEN buyer IS NOT NULL THEN 1 END) as valid_campaigns,
    COUNT(CASE WHEN buyer IS NULL THEN 1 END) as excluded_campaigns,
    COUNT(CASE WHEN impression_goal <= 0 THEN 1 END) as invalid_goals,
    COUNT(CASE WHEN start_date >= end_date THEN 1 END) as invalid_dates
  FROM campaigns_upload_staging
)

SELECT
  *,
  ROUND((valid_campaigns::FLOAT / total_uploads * 100), 1) as validation_success_rate
FROM upload_quality;
```

### Runtime Data Integrity:
```sql
-- Campaign-reporting data alignment check
SELECT
  'Missing reporting data' as issue_type,
  COUNT(*) as affected_campaigns,
  STRING_AGG(campaign_name, ', ' ORDER BY campaign_name) as examples
FROM campaigns c
LEFT JOIN reporting_data r ON (c.campaign_id = r.campaign_id OR c.campaign_id = r.deal_id)
WHERE c.end_date < NOW()
  AND c.buyer IS NOT NULL
  AND r.campaign_id IS NULL
  AND r.deal_id IS NULL
GROUP BY issue_type

UNION ALL

SELECT
  'Reporting without campaign' as issue_type,
  COUNT(DISTINCT COALESCE(r.campaign_id, r.deal_id)) as affected_records,
  STRING_AGG(DISTINCT COALESCE(r.campaign_id, r.deal_id), ', ') as examples
FROM reporting_data r
LEFT JOIN campaigns c ON (r.campaign_id = c.campaign_id OR r.deal_id = c.campaign_id)
WHERE c.campaign_id IS NULL
GROUP BY issue_type;
```

---

## DAR-009: API Service Architecture

### DataAggregationService Structure:
```javascript
class DataAggregationService {
  constructor(dbConnection, cacheService) {
    this.db = dbConnection;
    this.cache = cacheService;
  }

  // Primary visualization data
  async getFulfillmentGaps(filters = {}) {
    const cacheKey = this.buildCacheKey('fulfillment', filters);

    if (await this.cache.has(cacheKey)) {
      return await this.cache.get(cacheKey);
    }

    const query = this.buildFulfillmentQuery(filters);
    const results = await this.db.query(query);

    await this.cache.set(cacheKey, results, CACHE_CONFIG.fulfillmentGaps.ttl);
    return results;
  }

  // Temporal trend analysis
  async getTemporalTrends(purchaseType = null, timeWindow = 30) {
    const cacheKey = `temporal_${purchaseType}_${timeWindow}`;

    if (await this.cache.has(cacheKey)) {
      return await this.cache.get(cacheKey);
    }

    const query = this.buildTemporalQuery(purchaseType, timeWindow);
    const results = await this.db.query(query);

    // Add trend classification
    results.forEach(row => {
      row.trendDirection = this.classifyTrend(row.trend_change_7day);
    });

    await this.cache.set(cacheKey, results, CACHE_CONFIG.temporalTrends.ttl);
    return results;
  }

  // Campaign drill-down analysis
  async getCampaignDetails(campaignId, analysisType = 'temporal') {
    const cacheKey = `campaign_${campaignId}_${analysisType}`;

    if (await this.cache.has(cacheKey)) {
      return await this.cache.get(cacheKey);
    }

    let query;
    switch (analysisType) {
      case 'temporal':
        query = this.buildCampaignTemporalQuery(campaignId);
        break;
      case 'site':
        query = this.buildCampaignSiteQuery(campaignId);
        break;
      case 'hourly':
        query = this.buildCampaignHourlyQuery(campaignId);
        break;
    }

    const results = await this.db.query(query);
    await this.cache.set(cacheKey, results, CACHE_CONFIG.campaignDetails.ttl);
    return results;
  }

  // Data quality validation
  async validateUploadData(uploadData) {
    const validationQuery = this.buildUploadValidationQuery();
    return await this.db.query(validationQuery, uploadData);
  }
}
```

---

## DAR-010: UTC Timezone Handling

**Business Rule:** All datetime data processed in UTC throughout the system.

**Implementation:**
- **XLSX Upload:** Convert any local dates to UTC during import
- **API Data:** Already provided in UTC format (`2025-08-04T00:00:00.000Z`)
- **Database Storage:** All timestamp columns in UTC
- **Aggregation Queries:** Use UTC functions for date calculations
- **Frontend Display:** Convert to local timezone only for user display

**Query Pattern:**
```sql
-- Temporal aggregations in UTC
DATE(r.date_hour) as performance_date,  -- UTC date extraction
EXTRACT(HOUR FROM r.date_hour) as hour  -- UTC hour extraction

-- Time window filtering in UTC
WHERE r.date_hour >= NOW() - INTERVAL $time_window DAY  -- UTC comparison
```

---

## DAR-011: CRITICAL Database Schema Corrections

**MANDATORY CORRECTIONS:** Fix fundamental data structure misconceptions

**CORRECTED Campaign Table Schema:**
```sql
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    impression_goal INTEGER NOT NULL CHECK (impression_goal BETWEEN 1 AND 2000000000),
    runtime TEXT NOT NULL,  -- Format: "START_DATE-END_DATE" or "ASAP-END_DATE"
    buyer TEXT,  -- 'Not set' = campaign, other values = deal
    -- Optional reference fields (NOT primary analysis focus)
    budget DECIMAL(15,2),
    cpm DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**CRITICAL FIELD CORRECTIONS:**

**1. impression_goal Field:**
```sql
-- WRONG (DO NOT IMPLEMENT)
impression_goal TEXT DEFAULT '1-2000000000'

-- CORRECT (IMPLEMENT THIS)
impression_goal INTEGER NOT NULL CHECK (impression_goal BETWEEN 1 AND 2000000000)

-- Example values:
-- 1500000 (one and a half million impressions)
-- 250000 (quarter million impressions)
-- 2000000000 (two billion impressions - maximum)
```

**2. runtime Field:**
```sql
-- WRONG (DO NOT IMPLEMENT)
start_date DATE,
end_date DATE

-- CORRECT (IMPLEMENT THIS)
runtime TEXT NOT NULL

-- Example values:
-- "14.01.2025-26.01.2025" (standard date range)
-- "ASAP-14.12.2025" (ASAP start date)
-- "01.03.2025-31.03.2025" (March campaign)

-- Runtime parsing for queries:
CASE
  WHEN runtime LIKE 'ASAP-%' THEN
    CURRENT_DATE as effective_start_date,
    TO_DATE(SPLIT_PART(runtime, '-', 2), 'DD.MM.YYYY') as end_date
  ELSE
    TO_DATE(SPLIT_PART(runtime, '-', 1), 'DD.MM.YYYY') as start_date,
    TO_DATE(SPLIT_PART(runtime, '-', 2), 'DD.MM.YYYY') as end_date
END
```

**3. Budget/CPM De-emphasis:**
```sql
-- These fields exist as reference data only
-- NOT used for primary fulfillment analysis
budget DECIMAL(15,2),     -- Optional, secondary importance
cpm DECIMAL(10,4),        -- Optional, secondary importance

-- Primary analysis focuses on:
-- fulfillment_percentage = (delivered_impressions / impression_goal) * 100
-- impression_shortfall = impression_goal - delivered_impressions
```

**CORRECTED Query Patterns:**
```sql
-- Primary fulfillment analysis query
SELECT
    c.campaign_id,
    c.campaign_name,
    c.impression_goal,  -- INTEGER field
    c.runtime,          -- TEXT field to be parsed

    -- Parse runtime for date filtering
    CASE
      WHEN c.runtime LIKE 'ASAP-%' THEN
        TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
      ELSE
        TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
    END as campaign_end_date,

    -- Core fulfillment calculations
    COALESCE(SUM(r.total_impressions), 0) as delivered_impressions,
    (c.impression_goal - COALESCE(SUM(r.total_impressions), 0)) as impression_shortfall,

    CASE
      WHEN c.impression_goal > 0 THEN
        (COALESCE(SUM(r.total_impressions), 0)::FLOAT / c.impression_goal * 100)
      ELSE 0
    END as fulfillment_percentage

FROM campaigns c
LEFT JOIN reporting_data r ON (c.campaign_id = r.campaign_id OR c.campaign_id = r.deal_id)
WHERE
    -- Filter completed campaigns using parsed end date
    CASE
      WHEN c.runtime LIKE 'ASAP-%' THEN
        TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
      ELSE
        TO_DATE(SPLIT_PART(c.runtime, '-', 2), 'DD.MM.YYYY')
    END < CURRENT_DATE
    AND c.buyer IS NOT NULL
GROUP BY c.campaign_id, c.campaign_name, c.impression_goal, c.runtime, c.buyer
ORDER BY impression_shortfall DESC;  -- Worst fulfillment first
```

**Upload Validation Corrections:**
```sql
-- Validate impression_goal is proper integer
SELECT
    COUNT(*) as total_uploads,
    COUNT(CASE
        WHEN impression_goal IS NOT NULL
        AND impression_goal BETWEEN 1 AND 2000000000
        THEN 1
    END) as valid_impression_goals,
    COUNT(CASE
        WHEN runtime IS NOT NULL
        AND runtime ~ '^(ASAP|\d{2}\.\d{2}\.\d{4})-\d{2}\.\d{2}\.\d{4}$'
        THEN 1
    END) as valid_runtime_formats
FROM campaigns_upload_staging;
```

---

## Implementation Checklist

### Database Schema Requirements:
- [ ] Campaign table with buyer field validation
- [ ] Reporting data table with dual purchase type fields
- [ ] Appropriate indexes for performance optimization
- [ ] Data quality validation constraints

### API Endpoints Required:
- [ ] `/api/fulfillment-gaps` - Primary visualization data
- [ ] `/api/temporal-trends` - Rolling window analysis
- [ ] `/api/campaign-details/{id}` - Individual campaign drill-down
- [ ] `/api/upload-validation` - XLSX data quality check

### Caching Implementation:
- [ ] Redis/memory cache for aggregation results
- [ ] Cache invalidation strategy for data updates
- [ ] Performance monitoring for cache hit rates

### Data Quality Monitoring:
- [ ] Upload validation reporting
- [ ] Runtime data integrity checks
- [ ] Automated alerts for data quality issues

---

*This document should be updated when data aggregation patterns change or new analytical requirements emerge through discovery.*