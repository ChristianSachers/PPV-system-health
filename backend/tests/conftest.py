"""
Pytest Configuration for Campaign Data Foundation TDD Testing

This configuration provides:
1. Database fixtures with transaction isolation
2. FastAPI test client setup
3. Campaign completion validation with mocked current date
4. XLSX file processing test utilities
5. Comprehensive test data injection

Critical for discovery-driven TDD: Enables hypothesis testing about Runtime
parsing and classification while maintaining test isolation and repeatability.
"""

import pytest
import asyncio
from datetime import datetime, date
from typing import Generator, AsyncGenerator
from unittest.mock import patch
import tempfile
import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your app components (now implemented)
from app.main import app
from app.database import get_db, Base
from app.models.campaign import Campaign, UploadSession
# from app.services.runtime_parser import RuntimeParser  # Will be implemented
# from app.services.campaign_classifier import CampaignClassifier  # Will be implemented

from .fixtures.campaign_test_data import (
    RuntimeFormat,
    CampaignClassificationData,
    UUIDTestData,
    DataConversionTestData,
    ComprehensiveCampaignFixtures
)


# Test Database Configuration
SQLITE_TEST_DATABASE_URL = "sqlite:///./test_campaign_data.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db_engine():
    """
    Create a test database engine with transaction isolation.

    Each test gets a fresh database state, critical for testing
    campaign completion validation with different current dates.
    """
    engine = create_engine(
        SQLITE_TEST_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Clean up
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_campaign_data.db"):
        os.remove("./test_campaign_data.db")


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """
    Create a test database session with transaction rollback.

    Ensures test isolation - each test gets clean database state.
    Critical for testing campaign completion validation scenarios.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_client(test_db_session):
    """
    Create FastAPI test client with database dependency override.

    Enables testing API endpoints with isolated database state.
    """
    def override_get_db():
        try:
            yield test_db_session
        finally:
            test_db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clean up
    app.dependency_overrides.clear()


class MockedDateContext:
    """
    Context manager for testing campaign completion validation.

    Enables testing "current date" scenarios without system dependency.
    Critical for testing business rule: campaigns with end_date > current_date
    are excluded from analysis.
    """

    def __init__(self, mock_current_date: date):
        self.mock_current_date = mock_current_date
        self.patcher = None

    def __enter__(self):
        # Mock date.today() in the campaign model module
        self.patcher = patch('app.models.campaign.date')
        mock_date = self.patcher.start()
        mock_date.today.return_value = self.mock_current_date
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.patcher:
            self.patcher.stop()


@pytest.fixture
def mock_current_date():
    """
    Factory fixture for mocking current date in tests.

    Usage:
        def test_campaign_completion(mock_current_date):
            with mock_current_date(date(2025, 1, 15)):
                # Test with current date = 2025-01-15
                # Campaigns ending after 2025-01-15 should be excluded
    """
    def _mock_date(test_date: date):
        return MockedDateContext(test_date)

    return _mock_date


@pytest.fixture
def temp_xlsx_file():
    """
    Create temporary XLSX file for testing file upload scenarios.

    Returns path to temporary file that gets cleaned up after test.
    Critical for testing XLSX processing without file system pollution.
    """
    temp_file = tempfile.NamedTemporaryFile(
        suffix='.xlsx',
        delete=False
    )
    temp_file.close()

    yield temp_file.name

    # Clean up
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def sample_xlsx_data():
    """
    Provides sample XLSX data in the exact format expected from real files.

    This data represents the complexity of real campaign data:
    - Mixed Runtime formats (ASAP vs standard)
    - European number formatting
    - Complex buyer strings
    - Valid UUID formats
    """
    return [
        {
            "Deal/Campaign name": "2025_10147_0303_1_PV Promotion | UML | GIGA | CN-Autorinnen-Ausschreibung 2025",
            "Runtime": "ASAP-30.06.2025",
            "Impression goal": "2000000000",
            "Budget €": "2396690,38",
            "CPM €": "1,183",
            "Deal/Campaign ID": "56cc787c-a703-4cd3-995a-4b42eb408dfb",
            "Buyer": "Not set"
        },
        {
            "Deal/Campaign name": "Summer Campaign 2025 | Fashion | Premium Inventory",
            "Runtime": "07.07.2025-24.07.2025",
            "Impression goal": "1500000",
            "Budget €": "125000,50",
            "CPM €": "2,45",
            "Deal/Campaign ID": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "Buyer": "DENTSU_AEGIS < Easymedia_rtb (Seat 608194)"
        },
        {
            "Deal/Campaign name": "Completed Q1 Campaign 2024 | Tech | Mobile",
            "Runtime": "15.02.2024-28.02.2024",
            "Impression goal": "750000",
            "Budget €": "45000,00",
            "CPM €": "0,95",
            "Deal/Campaign ID": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
            "Buyer": "Not set"
        }
    ]


# Test Data Provider Fixtures (from our comprehensive fixtures)
@pytest.fixture
def runtime_formats():
    """Provides all Runtime format test cases for parametrized testing"""
    return {
        'asap': RuntimeFormat.ASAP_FORMATS,
        'standard': RuntimeFormat.STANDARD_FORMATS,
        'malformed': RuntimeFormat.MALFORMED_FORMATS
    }


@pytest.fixture
def classification_data():
    """Provides Campaign vs Deal classification test data"""
    return {
        'campaigns': CampaignClassificationData.CAMPAIGNS,
        'deals': CampaignClassificationData.DEALS
    }


@pytest.fixture
def uuid_validation_data():
    """Provides UUID validation test cases"""
    return {
        'valid': UUIDTestData.VALID_UUIDS,
        'invalid': UUIDTestData.INVALID_UUIDS
    }


@pytest.fixture
def data_conversion_cases():
    """Provides data conversion test cases for European number formats"""
    return {
        'budgets': DataConversionTestData.BUDGET_FORMATS,
        'impression_goals': DataConversionTestData.IMPRESSION_GOAL_FORMATS
    }


@pytest.fixture
def sample_campaigns():
    """Provides complete campaign fixtures for integration tests"""
    return ComprehensiveCampaignFixtures.get_sample_campaigns()


@pytest.fixture
def malformed_campaigns():
    """Provides malformed campaign data for error handling tests"""
    return ComprehensiveCampaignFixtures.get_malformed_campaigns()


# Campaign Completion Testing Scenarios
@pytest.fixture
def campaign_completion_scenarios():
    """
    Provides test scenarios for campaign completion validation.

    Critical business rule: Campaigns with end_date > current_date
    cannot be included in analysis.

    These scenarios test edge cases around the current date boundary.
    """
    return [
        {
            "description": "Campaign ending today should be included",
            "current_date": date(2025, 6, 30),
            "campaign_end_date": date(2025, 6, 30),
            "expected_is_running": False,  # Ends today = completed
            "expected_included_in_analysis": True
        },
        {
            "description": "Campaign ending tomorrow should be excluded",
            "current_date": date(2025, 6, 30),
            "campaign_end_date": date(2025, 7, 1),
            "expected_is_running": True,  # Ends tomorrow = running
            "expected_included_in_analysis": False
        },
        {
            "description": "Campaign ended yesterday should be included",
            "current_date": date(2025, 6, 30),
            "campaign_end_date": date(2025, 6, 29),
            "expected_is_running": False,  # Ended yesterday = completed
            "expected_included_in_analysis": True
        },
        {
            "description": "ASAP campaign ending in future should be excluded",
            "current_date": date(2025, 1, 15),
            "campaign_end_date": date(2025, 6, 30),  # ASAP-30.06.2025
            "expected_is_running": True,
            "expected_included_in_analysis": False
        }
    ]


# Test Configuration
def pytest_configure(config):
    """Configure pytest with custom markers for test organization"""
    config.addinivalue_line(
        "markers",
        "runtime_parsing: marks tests for Runtime parsing functionality"
    )
    config.addinivalue_line(
        "markers",
        "classification: marks tests for Campaign vs Deal classification"
    )
    config.addinivalue_line(
        "markers",
        "uuid_validation: marks tests for UUID validation and preservation"
    )
    config.addinivalue_line(
        "markers",
        "data_conversion: marks tests for XLSX data conversion"
    )
    config.addinivalue_line(
        "markers",
        "completion_validation: marks tests for campaign completion validation"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks integration tests requiring full system"
    )
    config.addinivalue_line(
        "markers",
        "discovery: marks discovery-oriented tests for pattern exploration"
    )


# Test Helper Functions
class TestHelpers:
    """Utility functions for common test operations"""

    @staticmethod
    def create_campaign_with_runtime(runtime_string: str, **kwargs):
        """
        Helper to create campaign test data with specific runtime.

        Useful for parametrized tests of Runtime parsing scenarios.
        """
        base_campaign = {
            "name": "Test Campaign",
            "runtime": runtime_string,
            "impression_goal": "1000000",
            "budget_eur": "10000,00",
            "cpm_eur": "2,00",
            "id": "56cc787c-a703-4cd3-995a-4b42eb408dfb",
            "buyer": "Not set"
        }
        base_campaign.update(kwargs)
        return base_campaign

    @staticmethod
    def assert_runtime_parsing_result(parsed_result, expected_start, expected_end):
        """
        Helper to assert Runtime parsing results consistently.

        Handles None values for ASAP start dates and date comparisons.
        """
        if expected_start is None:
            assert parsed_result.start_date is None
        else:
            assert parsed_result.start_date == expected_start

        assert parsed_result.end_date == expected_end

    @staticmethod
    def assert_campaign_classification(classification_result, expected_type):
        """
        Helper to assert Campaign vs Deal classification consistently.
        """
        assert classification_result.campaign_type == expected_type


@pytest.fixture
def test_helpers():
    """Provides TestHelpers instance for test convenience"""
    return TestHelpers


# Mock Services for Testing
@pytest.fixture
def mock_runtime_parser():
    """
    Mock RuntimeParser for testing parser integration.

    Enables testing without implementing the actual parser service.
    Backend-engineer will replace this with real service integration.
    """
    class MockRuntimeParser:
        def parse(self, runtime_string: str):
            # This will be replaced with actual implementation
            # For now, return mock result based on test data
            pass

    return MockRuntimeParser()


@pytest.fixture
def mock_campaign_classifier():
    """
    Mock CampaignClassifier for testing classification logic.

    Enables testing without implementing the actual classifier service.
    """
    class MockCampaignClassifier:
        def classify(self, buyer: str):
            # This will be replaced with actual implementation
            return "campaign" if buyer == "Not set" else "deal"

    return MockCampaignClassifier()


# Environment Setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Automatically set up test environment for all tests.

    Ensures consistent test environment across all test modules.
    """
    # Set test environment variables
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = SQLITE_TEST_DATABASE_URL

    yield

    # Clean up
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]