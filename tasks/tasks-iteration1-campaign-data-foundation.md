## Tasks: Iteration 1 - Campaign Data Foundation

**Business Value:** PM can upload XLSX campaign files and see structured, validated campaign data

## Relevant Files

- `backend/main.py` - FastAPI application entry point with CORS and middleware configuration
- `backend/database/connection.py` - PostgreSQL connection management and database configuration
- `backend/database/models.py` - SQLAlchemy models for campaigns and upload tracking
- `backend/database/migrations/001_initial_schema.sql` - Database schema creation script
- `backend/services/xlsx_processor.py` - XLSX file parsing and validation service
- `backend/services/campaign_validator.py` - Campaign data validation logic and business rules
- `backend/routes/upload.py` - File upload API endpoints
- `backend/routes/campaigns.py` - Campaign data retrieval API endpoints
- `backend/tests/test_xlsx_processor.py` - Unit tests for XLSX processing
- `backend/tests/test_campaign_validator.py` - Unit tests for campaign validation
- `backend/tests/test_upload_routes.py` - API endpoint tests for upload functionality
- `frontend/src/App.tsx` - Main React application component with routing
- `frontend/src/components/UploadInterface.tsx` - XLSX file upload UI component
- `frontend/src/components/CampaignDataTable.tsx` - Campaign data display table component
- `frontend/src/components/ValidationReport.tsx` - Data quality reporting component
- `frontend/src/services/api.ts` - API client for backend communication
- `frontend/src/types/campaign.ts` - TypeScript interfaces for campaign data
- `frontend/src/tests/UploadInterface.test.tsx` - Unit tests for upload component
- `frontend/src/tests/CampaignDataTable.test.tsx` - Unit tests for data display
- `docker-compose.yml` - Development environment with PostgreSQL database
- `backend/requirements.txt` - Python dependencies (FastAPI, SQLAlchemy, pandas, openpyxl)
- `frontend/package.json` - Node.js dependencies (React, TypeScript, Ant Design, axios)

### Notes

- Unit tests should be placed alongside the code files they are testing
- Use `pytest backend/tests/` to run backend tests
- Use `npm test` in frontend directory to run frontend tests
- XLSX processing requires pandas and openpyxl for robust file handling
- Campaign vs Deal classification: `buyer = 'Not set'` = campaign, else deal
- UUID validation is critical for data integrity (campaign_id field)

## Tasks

- [ ] 1.0 Project Infrastructure & Development Environment Setup
  - [ ] 1.1 Initialize backend directory structure with FastAPI project layout
  - [ ] 1.2 Create frontend directory structure with Create React App + TypeScript template
  - [ ] 1.3 Set up docker-compose.yml with PostgreSQL database service
  - [ ] 1.4 Configure backend requirements.txt with FastAPI, SQLAlchemy, pandas, openpyxl, pytest
  - [ ] 1.5 Configure frontend package.json with React, TypeScript, Ant Design, axios, testing libraries
  - [ ] 1.6 Create .env files for database connection strings and API configuration
  - [ ] 1.7 Set up development scripts for running backend/frontend/database together

- [ ] 2.0 Database Schema Design & Campaign Data Model
  - [ ] 2.1 Design campaigns table schema based on XLSX data structure from PRD
  - [ ] 2.2 Create upload_sessions table for tracking file upload status and validation results
  - [ ] 2.3 Write initial database migration script (001_initial_schema.sql)
  - [ ] 2.4 Implement SQLAlchemy models for Campaign and UploadSession entities
  - [ ] 2.5 Create database connection management with environment-based configuration
  - [ ] 2.6 Add database indexes for UUID lookups and buyer field queries
  - [ ] 2.7 Write unit tests for database models and connection management

- [ ] 3.0 Backend API Foundation with FastAPI
  - [ ] 3.1 Create FastAPI application instance with CORS middleware for frontend integration
  - [ ] 3.2 Set up application startup/shutdown handlers for database connection lifecycle
  - [ ] 3.3 Implement basic health check endpoint for application monitoring
  - [ ] 3.4 Configure request/response logging middleware for debugging
  - [ ] 3.5 Set up error handling middleware with structured error responses
  - [ ] 3.6 Create base response models for consistent API response format
  - [ ] 3.7 Write integration tests for FastAPI application setup and middleware

- [ ] 4.0 XLSX Upload Processing & Validation Pipeline
  - [ ] 4.1 Implement XLSX file parser using pandas to read campaign data sheets
  - [ ] 4.2 Create campaign data validator with business rules (UUID format, required fields)
  - [ ] 4.3 Implement buyer field classification logic (campaign vs deal determination)
  - [ ] 4.4 Build data quality reporting system (count valid/invalid records, error details)
  - [ ] 4.5 Create upload processing service that coordinates parsing, validation, and storage
  - [ ] 4.6 Implement UUID-based deduplication logic for incremental campaign updates
  - [ ] 4.7 Write comprehensive unit tests for XLSX processing and validation logic

- [ ] 5.0 Frontend Application Framework with React + TypeScript
  - [ ] 5.1 Set up React application with routing using React Router for multi-page navigation
  - [ ] 5.2 Configure Ant Design theme and component library integration
  - [ ] 5.3 Create TypeScript interfaces for campaign data matching backend models
  - [ ] 5.4 Set up API client service with axios for backend communication
  - [ ] 5.5 Implement global state management for upload status and campaign data
  - [ ] 5.6 Create responsive layout structure with header, navigation, and content areas
  - [ ] 5.7 Set up frontend testing framework with React Testing Library and Jest

- [ ] 6.0 Campaign Data Display Interface
  - [ ] 6.1 Create XLSX file upload component with drag-and-drop functionality using Ant Design Upload
  - [ ] 6.2 Implement campaign data table with sorting, filtering, and pagination
  - [ ] 6.3 Add campaign vs deal visual indicators based on buyer field classification
  - [ ] 6.4 Create detailed campaign view modal for individual campaign inspection
  - [ ] 6.5 Implement search functionality for campaign names and IDs
  - [ ] 6.6 Add data export functionality for filtered campaign datasets
  - [ ] 6.7 Write unit tests for all UI components and user interactions

- [ ] 7.0 Data Quality Reporting & Validation Feedback System
  - [ ] 7.1 Create upload status tracking with progress indicators during file processing
  - [ ] 7.2 Implement validation report component showing successful/failed record counts
  - [ ] 7.3 Build detailed error reporting with specific validation failure reasons
  - [ ] 7.4 Create data quality dashboard showing statistics (total campaigns, deals, excluded records)
  - [ ] 7.5 Implement real-time upload progress updates using WebSocket or polling
  - [ ] 7.6 Add notification system for upload completion and validation results
  - [ ] 7.7 Write integration tests for complete upload-to-display workflow