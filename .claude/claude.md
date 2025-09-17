# Claude Code Project Configuration

This file contains project-specific information and commands for Claude Code.

## Project Overview
PPV System Health Monitor - A tactical system analysis tool designed to distinguish between systemic delivery problems and expected resource constraints. This is a 1-year solution focused on enabling product managers to conduct root cause analysis on campaign fulfillment patterns to identify infrastructure vs capacity issues through iterative discovery.
- /Users/christiansachers/Library/CloudStorage/OneDrive-StroeerGlobalDirectory/VibeCoding/PPV-Fulfillment-Monitor_V2/tasks/prd-campaign-fulfillment-tracking.md

**Core Mission:** Answer "Is this a system problem or a resource problem?"

**Core Capabilities:**
- System health pattern recognition and correlation analysis
- High-density analytical dashboards for investigation workflows
- Flexible data exploration supporting hypothesis-driven discovery
- Root cause analysis tools for distinguishing systemic vs resource constraint issues
- Investigation drill-down patterns for product manager workflows
- XLSX campaign/deal data upload and automated reporting API integration

**Architecture:** Web application with PostgreSQL persistence, FastAPI backend, React TypeScript frontend, and external reporting API integration.

## System Health Analysis Framework

**Primary Purpose:** Enable product managers to distinguish between systemic problems and expected resource constraints through pattern recognition and root cause analysis.

### Investigation Methodology
- **Pattern Recognition:** Identify correlations between campaign load and performance metrics
- **Anomaly Detection:** Distinguish between expected underperformance and problematic patterns
- **Root Cause Analysis:** Support hypothesis-driven investigation workflows
- **Trend Analysis:** Time-based pattern recognition for system health evolution
- **Comparative Analysis:** Load vs performance relationship validation

### Target User Workflows
- **System Health Assessment:** Quick evaluation of overall system performance patterns
- **Investigation Drill-downs:** Detailed analysis when anomalies are detected
- **Pattern Validation:** Confirm whether issues are systemic vs resource-related
- **Hypothesis Testing:** Iterative exploration to understand system behavior

### Information Architecture Principles
- **High-Density Analytics:** Maximize information per screen for investigation efficiency
- **Investigation-First Design:** UI optimized for analytical workflows, not operational simplicity
- **Flexible Pattern Recognition:** Adaptive analysis tools that support discovery-driven exploration
- **Multi-Dimensional Analysis:** Combined correlation views, trend analysis, and drill-down capabilities

### Discovery-Driven Development Approach
- **Iterative Requirement Evolution:** Requirements emerge through exploration and learning
- **Hypothesis-Driven Features:** Build tools to test assumptions about system behavior
- **Safe Experimentation:** TDD discipline enables confident iteration during discovery
- **Learning Documentation:** Capture insights and patterns as system understanding grows

## User Rules - MUST BE RESPECTED AT ALL TIMES!
- the first step of any change is to create a test case, no production code is allowed to be written without a test case upfront
- never assume anything. if you have questions, directly ask the User
- always use the appropriate agent for each task
- commit messages must be short, bulletpoint style and descriptive
- use the challenging-mentor output style

### System Health Analysis Specific Rules
- **solution-architect is mandatory first contact** for any system health analysis work
- **challenge every technical assumption** before implementing
- **break every task into 2-minute iterations** with progress updates
- **tactical mindset required** - optimize for immediate business value, not perfect architecture
- **validate analysis methodology** before technical implementation
- **single source of truth enforcement** - XLSX for master data, API for reporting data
- **no feature creep** - stick to system health investigation core mission
- **more information is better** - prioritize high-density analytical interfaces over simplicity
- **discovery-driven development** - requirements emerge through iterative exploration

### File Organization & Component Design - MUST BE RESPECTED AT ALL TIMES
  - **Cohesion Over Size**: Keep related functionality together. A 400-line component handling one user workflow is better than 4 artificially split 100-line components
  - **Single Responsibility**: Each file should have one clear, well-defined purpose that can be explained in one sentence
  - **Extract for Reusability**: If logic could be reused elsewhere, extract it to custom hooks, utilities, or services
  - **UI Component Guidelines**:
    - React components up to 500 lines are acceptable if handling a single user workflow
    - Extract state management to custom hooks when logic exceeds 150 lines
    - Split only when handling multiple unrelated features
  - **Service/Utility Guidelines**:
    - Keep focused utilities under 200 lines
    - Split when handling multiple unrelated domains
    - Configuration and type files have no size limits

  ### Code Quality Indicators
  - **Readability Test**: Can the file's purpose be understood within 30 seconds of opening it?
  - **Testability**: Can the component/function be tested effectively with clear, focused test cases?
  - **Naming Clarity**: Functions, variables, and components should have descriptive names that explain their purpose
  - **TypeScript Usage**: All interfaces, props, and function signatures must be properly typed

  ### When to Split Components
  - **Multiple User Workflows**: Component handles distinct, unrelated user tasks
  - **Mixed Concerns**: Component handles both UI rendering and business logic that could be extracted
  - **Repeated Patterns**: When similar logic appears in multiple places, extract to shared utilities
  - **Testing Complexity**: When tests become unwieldy due to component doing too many things

  ### AI Agent Optimization
  - **Clear Function Boundaries**: Use descriptive function names and proper separation
  - **Comprehensive TypeScript**: Type everything to help AI understand intent and interfaces
  - **Meaningful Comments**: Explain complex business logic, not obvious code
  - **Consistent Patterns**: Follow established patterns within the codebase for predictability

  ### Refactoring Triggers
  - **Explain Before Enforcing**: Before suggesting splits, explain why the current structure might be improved
  - **Quality Over Metrics**: Focus on improving maintainability, testability, and readability
  - **Context Matters**: Consider the domain complexity - financial calculations, UI workflows, and data processing naturally require larger components
  - **User Value**: Prioritize changes that improve user experience or developer productivity

  ### Testing Requirements
  - **Test-Driven Development**: Write tests before implementing new features
  - **Component Testing**: Test user interactions and state changes, not implementation details
  - **Integration Testing**: Verify API communication and data flow between components
  - **Accessibility Testing**: Ensure keyboard navigation and screen reader compatibility

## System Health Analysis Project Rules

### Data Architecture Principles
- **XLSX as Master Data Source:** Campaign metadata (name, runtime, impression goal, budget, CPM, buyer) comes from uploaded files
- **API as Reporting Source:** Delivery metrics (total impressions, purchase type, detailed performance data) come from reporting API
- **UUID-Based Identity:** Deal/Campaign IDs are immutable UUIDs that serve as primary keys
- **Upsert Logic:** Insert new campaigns, update existing ones field-by-field, never modify IDs
- **Scale Constraints:** System designed for single user, max 300 concurrent campaigns
- **Analytical Data Separation:** Clear distinction between operational data and analytical insights

### System Health Analysis Guidelines
- **Campaign vs Deal Detection:** "Buyer" field determines type ("Not set" = Campaign, specific value = Deal)
- **Fulfillment Calculation:** (Total Impressions / Impression Goal) * 100
- **Pattern Recognition:** Flexible correlation analysis between load and performance patterns
- **Investigation Framework:** Support for hypothesis-driven root cause analysis
- **Time Granularity:** Multi-dimensional temporal analysis for pattern detection
- **Anomaly Detection:** Distinguish systemic issues from expected resource constraints

### Tactical Solution Mindset
- **1-Year Lifespan:** Optimize for immediate business value, not long-term maintainability
- **Single User Focus:** No authentication, multi-tenancy, or complex access controls needed
- **Discovery-First Approach:** Build analytical tools that evolve with understanding
- **Learning Tool:** Insights from this system will inform production tech stack solutions
- **Investigation-Optimized:** Prioritize analytical depth over operational simplicity

## Project-Specific Agents

**Agent Definitions:** See `.claude/agents/` directory for detailed specifications.

### Primary Workflow:
1. **ALWAYS start with `solution-architect`** - Enhanced educational mentor specialized for CS graduates returning to coding
2. **Specialized agents used only after solution-architect approval:**
   - `backend-engineer` - System health analysis API development and data processing
   - `ui-design-expert` - Analytical dashboard design and investigation interface patterns
   - `tdd-test-engineer` - Discovery-driven testing and hypothesis validation

### Key Workflow Rules:
- **solution-architect is mandatory first contact** for all system health analysis work
- **Every task broken into 2-minute iterations** with progress updates
- **Educational approach required** - comprehensive explanations, visual diagrams, example-driven learning
- **Challenge-driven development** - assumptions questioned before implementation
- **Discovery-focused** - support for iterative exploration and hypothesis testing
- **Tactical solution focus** - optimize for immediate analytical insights over perfect architecture

## Key Commands

### Development
```bash
# Start both frontend and backend servers
./start-dev.sh

# Stop development servers
./stop-dev.sh
# Or use Ctrl+C to stop

# Backend only (FastAPI on port 8001)
cd backend && python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend only (React TypeScript on port 3001)
cd frontend && npm run dev

# Database operations (local PostgreSQL)
psql -d ppv_fulfillment_dev  # Connect to database
pg_dump ppv_fulfillment_dev > backup.sql  # Backup database
psql -d ppv_fulfillment_dev < backup.sql  # Restore database

# Run tests
npm test

# System health analysis specific operations
python backend/analyze_excel.py <file>  # Validate XLSX structure
python -m pytest backend/tests/integration/test_campaign_*.py  # System health analysis tests
python -m pytest backend/tests/integration/test_system_health_*.py  # Pattern recognition tests
```

### System Health Analysis Development Workflow
```bash
# MANDATORY WORKFLOW - ALWAYS START WITH SOLUTION-ARCHITECT
# Step 1: Present idea/request to solution-architect agent
# Step 2: Get architectural approval and iteration breakdown
# Step 3: Execute micro-iterations with specialized agents
# Step 4: Report progress and get next iteration guidance

# Example workflow:
# 1. "I want to fix the upload system" → solution-architect
# 2. Solution-architect challenges: "Fix vs rebuild? What's actually broken?"
# 3. Solution-architect defines 5 micro-tasks of 2 minutes each
# 4. upload-diagnostics-agent executes tasks 1-3
# 5. Solution-architect reviews progress and adjusts remaining tasks
```

### Build & Deploy
```bash
# Build frontend
cd frontend && npm run build

# Start production server
cd backend && python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

📁 Project Structure:
  ├── frontend/          # Client-side application
  │   ├── src/
  │   │   ├── components/   # Reusable UI components
  │   │   ├── pages/        # Route pages
  │   │   ├── hooks/        # Custom React hooks
  │   │   ├── services/     # API calls
  │   │   ├── utils/        # Helper functions
  │   │   ├── assets/       # Images, fonts, etc.
  │   │   └── styles/       # CSS/styling files
  │   └── public/           # Static assets
  │
  ├── backend/           # Server-side API
  │   ├── src/
  │   │   ├── routes/       # API endpoints
  │   │   ├── controllers/  # Request handlers
  │   │   ├── models/       # Database models
  │   │   ├── middleware/   # Auth, validation, etc.
  │   │   ├── services/     # Business logic
  │   │   ├── utils/        # Helper functions
  │   │   └── config/       # App configuration
  │   └── uploads/          # File upload storage
  │
  ├── database/          # Database management
  │   ├── migrations/       # Schema changes
  │   ├── seeds/           # Test data
  │   ├── schema/          # Database schema
  │   └── backups/         # Database backups
  │
  ├── shared/            # Common code
  │   ├── types/           # TypeScript types
  │   ├── constants/       # Shared constants
  │   └── utils/           # Shared utilities
  │
  ├── tests/             # Testing
  │   ├── unit/            # Unit tests
  │   ├── integration/     # Integration tests
  │   └── e2e/             # End-to-end tests
  │
  ├── uploads/           # Global upload storage
  ├── docs/              # Documentation
  └── [config files]     # .gitignore, docker-compose.yml, etc.

## Database
- Development: Local PostgreSQL 15 (installed via Homebrew)
- Database name: `ppv_fulfillment_dev`
- Connection: Local PostgreSQL server on default port 5432
- Production: Configured via environment variables

### System Health Analysis Schema
- **Primary Tables:** campaigns_deals (master data), reporting_metrics (API data), performance_details (hourly data), system_health_metrics (analysis data)
- **Key Relationships:** UUID-based foreign keys linking master data to reporting data and analytical insights
- **Data Sources:** Clear separation between XLSX-sourced fields, API-sourced fields, and computed analytical metrics
- **Migration Strategy:** Extend existing schema to support analytical data storage and pattern recognition
- **Analytical Tables:** Support for correlation analysis, pattern recognition results, and investigation history

## File Uploads
- Local development: `./uploads` and `./backend/uploads`
- Production: Cloud storage (S3, etc.)

## Environment Variables
Copy `.env.example` to `.env` and configure:
- Database credentials
- API keys
- File storage settings
