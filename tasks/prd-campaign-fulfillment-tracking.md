# PRD: System Health Analysis for Campaign Performance

## Introduction/Overview

This tool addresses the critical business problem of distinguishing between systemic delivery problems and expected resource constraints in advertising campaign performance. Currently, product managers lack the analytical framework to determine whether underperformance indicates infrastructure issues or normal capacity limitations. The system will enable pattern recognition analysis of campaign load vs. performance relationships through iterative discovery to identify root causes of delivery problems.

**Goal:** Create a tactical analytical solution (1-year lifespan) that enables product managers to conduct hypothesis-driven investigation of system health patterns, distinguishing between systemic issues requiring infrastructure fixes and expected resource constraints through flexible pattern recognition tools.

## Goals

1. **Enable System Health Pattern Recognition:** Build analytical tools to identify correlations between campaign load and performance patterns
2. **Support Root Cause Investigation:** Provide investigation workflows that help distinguish systemic issues from resource constraints
3. **Create Flexible Analysis Framework:** Support hypothesis-driven exploration where requirements emerge through iterative discovery
4. **Implement High-Density Analytical Dashboards:** Maximize information density for product manager investigation workflows
5. **Support Discovery-Driven Development:** Enable safe experimentation and pattern exploration through TDD discipline
6. **Fix Existing Upload Infrastructure:** Repair the current broken file upload system that fails to persist data to the database
7. **Maintain Data Integrity:** Ensure proper source-of-truth handling between XLSX master data and API reporting data

## User Stories

**As a product manager conducting system health analysis, I want to:**
- Analyze patterns between campaign load and performance to identify when underperformance indicates systemic issues vs. expected resource constraints
- Conduct hypothesis-driven investigation workflows to explore potential root causes of delivery problems
- Access high-density analytical dashboards that maximize information per screen for efficient investigation
- Drill down from system health alerts to detailed analysis views to validate whether issues are infrastructure-related
- Compare performance patterns across different load scenarios to understand system behavior under varying conditions
- Test hypotheses about system behavior through flexible analytical tools that support iterative discovery

**As a product manager building system understanding, I want to:**
- Explore data patterns without predefined constraints so I can discover insights through iterative analysis
- Build analytical models that evolve as my understanding of the system grows
- Document investigation findings and pattern recognition results for future reference
- Validate analytical assumptions through flexible correlation analysis and trend detection
- Access investigation workflows that guide systematic root cause analysis methodology

## Functional Requirements

### Core Upload & Data Management
1. The system must allow users to upload XLSX files with campaign/deal data
2. The system must validate XLSX file structure and data formats before processing
3. The system must parse the following columns from XLSX files:
   - "Deal/Campaign name" (string, e.g., "2025_31158_0058_1_Netzwerk_ALDI SÜD...")
   - "Deal/Campaign ID" (UUID format, e.g., "c99ab103-1b99-48f5-947c-a345b1c0cc93")
   - "Runtime" (date range format, e.g., "04.09.2025-06.09.2025")
   - "Impression goal" (integer, range 1-2000000000)
   - "Budget €" (integer without currency symbol)
   - "CPM €" (decimal up to 4 digits, e.g., "1,125")
   - "Buyer" (string, "Not set" indicates Campaign, specific value indicates Deal)
4. The system must implement upsert logic based on Deal/Campaign ID uniqueness
5. The system must perform field-by-field change detection for existing records
6. The system must never allow Deal/Campaign ID updates once persisted
7. The system must treat XLSX data as source of truth for: name, runtime, impression goal, budget, CPM, and buyer fields

### API Integration & Reporting
8. The system must trigger reporting API calls based on uploaded campaign/deal data
9. The system must retrieve different data sets for Campaigns vs. Deals:
   - **Campaigns:** Total Impressions, Core DSP Campaign name/ID, Campaign Purchase Type
   - **Deals:** Total Impressions, Deal Name/ID, Deal Purchase Type
10. The system must collect detailed delivery data for underperforming campaigns/deals:
    - Hourly granularity data (Date, Site, Bids, Auction Wins, Sync Group Plays)
11. The system must handle API data as source of truth for all reporting metrics
12. The system must verify API responses match requested Deal/Campaign IDs

### System Health Analysis & Pattern Recognition
13. The system must provide flexible correlation analysis between campaign load and performance patterns
14. The system must support hypothesis-driven investigation workflows with drill-down capabilities
15. The system must enable pattern recognition tools that help distinguish systemic issues from resource constraints
16. The system must provide high-density analytical dashboards optimized for investigation efficiency
17. The system must support iterative exploration where analytical requirements evolve through discovery
18. The system must enable comparative analysis across different load scenarios and time periods
19. The system must provide investigation workflow templates for systematic root cause analysis

### Analysis & Reporting
20. The system must calculate fulfillment percentages (Total Impressions / Impression Goal * 100)
21. The system must generate system health analysis showing:
    - Load vs performance correlation patterns
    - System health status indicators (healthy constraint vs systemic issue)
    - Pattern recognition results and anomaly detection
    - Investigation workflow progression and findings
22. The system must provide time-based pattern analysis:
    - Trend correlation analysis over configurable time windows
    - Load pattern evolution tracking
    - System behavior pattern recognition over time
23. The system must support flexible analytical filtering:
    - Dynamic filter criteria based on discovered patterns
    - Hypothesis-driven filter combinations
    - Extensible architecture for emergent analytical needs

### Data Integrity & Validation
24. The system must validate all data types and ranges before database insertion
25. The system must handle UUID format validation for Deal/Campaign IDs
26. The system must parse and validate date ranges in Runtime field
27. The system must handle decimal formatting for CPM values (accounting for comma as decimal separator)
28. The system must provide clear error messages for data validation failures

## Non-Goals (Out of Scope)

- **Long-term Production System:** This is a 1-year tactical solution, not a permanent platform
- **Multi-user Access Control:** Single-user application with no authentication requirements
- **Real-time Data Streaming:** Batch processing approach is sufficient for business needs
- **Advanced Data Warehousing:** Simple relational database storage is adequate
- **Mobile Responsiveness:** Desktop-focused interface is sufficient
- **Audit Trail/Version History:** Not required for initial business needs
- **Automated Alerting:** Manual report review is sufficient
- **Data Export Beyond Analysis:** Focus on visualization, not data extraction
- **Campaign Management Features:** Read-only analysis tool, not a campaign management system

## Design Considerations

### Analytical Interface Design
- **High-Density Information Architecture:** Maximize analytical information per screen for investigation efficiency
- **Investigation Workflow Navigation:** Seamless drill-down patterns from system health alerts to detailed analysis
- **Hypothesis Testing Interface:** Support for flexible pattern exploration and analytical experimentation
- **Discovery-Driven Dashboard Evolution:** Interface components that adapt as analytical understanding grows
- **Progress Indicators:** Show analysis processing and pattern recognition status to user
- **Error Display:** Clear validation error messages with specific analytical feedback

### System Health Visualization
- **Correlation Analysis Dashboards:** Load vs performance pattern visualization with interactive exploration
- **Pattern Recognition Display:** Visual indicators for systemic issues vs resource constraints
- **Investigation Workflow Charts:** Guided analysis paths for systematic root cause investigation
- **Comparative Analysis Views:** Side-by-side pattern comparison across different scenarios
- **Trend Pattern Analysis:** Multi-dimensional temporal analysis for system behavior recognition

## Technical Considerations

### Database Schema
- **Extend Existing Schema:** Build upon current database structure rather than creating parallel system
- **UUID Primary Keys:** Use Deal/Campaign ID as natural primary key with UUID validation
- **Decimal Precision:** Ensure proper handling of CPM decimal values and impression calculations
- **Date Range Storage:** Efficient storage and querying of runtime date ranges
- **Source of Truth Tracking:** Clear field ownership between XLSX and API data sources

### API Integration Architecture
- **Chunked Processing:** Handle up to 300 concurrent campaigns with batched API calls
- **Error Handling:** Robust retry logic for API failures
- **Rate Limiting:** Respect reporting API rate limits
- **Data Mapping:** Clear mapping between internal schema and external API responses

### Performance Requirements
- **Single User Load:** Optimize for single concurrent user, not high throughput
- **File Size Handling:** Support XLSX files with up to 300 campaigns/deals
- **Query Performance:** Efficient filtering and aggregation for reporting views
- **Background Processing:** Non-blocking upload processing with status updates

### Integration Points
- **Current Upload System:** Diagnose and repair existing upload infrastructure first
- **Database Connection:** Leverage existing PostgreSQL connection and ORM
- **Frontend Components:** Extend current React/TypeScript dashboard components
- **API Services:** Build upon existing service layer patterns

## Success Metrics

### Analytical Impact
- **Pattern Recognition Capability:** System successfully distinguishes systemic issues from resource constraints in 90%+ of analysis scenarios
- **Investigation Efficiency:** Product managers can complete root cause analysis workflows 75% faster than manual methods
- **Hypothesis Validation:** Support for iterative discovery enables successful pattern identification through exploratory analysis
- **System Health Understanding:** Clear insights into when underperformance indicates infrastructure vs capacity issues

### Technical Performance
- **Upload Success Rate:** 95%+ successful file uploads and data persistence
- **Analytical Processing Speed:** Complete analysis cycle (upload → API retrieval → pattern analysis) within 30 minutes for 300 campaigns
- **Investigation Responsiveness:** Drill-down analysis operations complete within 5 seconds for optimal investigation flow
- **System Reliability:** 99% uptime during business hours

### Discovery-Driven Development Success
- **Requirement Evolution:** System successfully adapts to emerging analytical requirements through iterative development
- **Safe Experimentation:** TDD discipline enables confident exploration without regression in existing functionality
- **Learning Documentation:** Analytical discoveries are captured and accessible for future investigation workflows
- **Flexible Analysis:** System supports hypothesis-driven exploration without predefined analytical constraints

## Open Questions

### Technical Implementation
1. **Current System Diagnosis:** What specific components in the existing upload system are failing? (Database connection, file processing, frontend submission?)
2. **Database Migration Strategy:** Do we need schema migrations for the new campaign/deal structure?
3. **API Endpoint Details:** What are the specific endpoint URLs, authentication methods, and rate limits for the reporting API?
4. **Error Recovery:** How should the system handle partial API failures (some campaigns succeed, others fail)?

### System Health Analysis Clarification
5. **Pattern Recognition Scope:** What types of correlations and patterns should the initial analysis focus on during discovery phase?
6. **Analysis Methodology:** What investigation workflow templates will be most valuable for systematic root cause analysis?
7. **Historical Pattern Analysis:** Should the system analyze historical patterns to establish baseline system health indicators?
8. **Threshold Flexibility:** How should the system handle dynamic thresholds that evolve as system understanding grows?

### Discovery-Driven Development
9. **Requirement Evolution:** How should the system capture and adapt to emerging analytical requirements during iterative development?
10. **Hypothesis Documentation:** What format should be used to document analytical hypotheses and investigation findings?
11. **Learning Integration:** How should discovered patterns be integrated back into the analytical framework for future investigations?

### Future Analytical Extensibility
12. **Pattern Recognition Enhancement:** What advanced analytical capabilities might be needed as system understanding develops?
13. **Integration Handoff:** What analytical insights format will be needed to transition findings to production infrastructure decisions?
14. **Investigation Workflow Evolution:** How should investigation templates evolve based on successful root cause analysis patterns?

---

**Next Steps:** Upon PRD approval, begin with implementing analytical framework foundation while diagnosing existing upload system infrastructure. Focus on creating flexible pattern recognition tools that support hypothesis-driven investigation workflows and discovery-driven development methodology.