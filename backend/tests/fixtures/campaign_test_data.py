"""
Campaign Test Data Fixtures for Runtime Parsing and Classification Testing

This module provides comprehensive test data that demonstrates the complexity of:
1. Runtime parsing (ASAP-DD.MM.YYYY vs DD.MM.YYYY-DD.MM.YYYY formats)
2. Campaign vs Deal classification (buyer='Not set' vs actual buyer)
3. UUID preservation and validation
4. European date formatting challenges
5. Budget/impression goal data conversion edge cases

Critical for discovery-driven TDD: These fixtures enable hypothesis testing
about data patterns while maintaining regression protection.
"""

from datetime import datetime, date
from uuid import UUID
import pytest
from typing import Dict, List, Any, Optional


class RuntimeFormat:
    """Test data demonstrating Runtime parsing complexity"""

    # ASAP format cases - start date undefined, end date specified
    ASAP_FORMATS = [
        {
            "runtime_string": "ASAP-30.06.2025",
            "expected_start": None,  # ASAP = undefined start
            "expected_end": date(2025, 6, 30),
            "expected_is_running": True,  # Assuming current date < 30.06.2025
            "description": "Standard ASAP format with June end date"
        },
        {
            "runtime_string": "ASAP-31.12.2025",
            "expected_start": None,
            "expected_end": date(2025, 12, 31),
            "expected_is_running": True,
            "description": "ASAP format with year-end date"
        },
        {
            "runtime_string": "ASAP-15.03.2024",  # Past date for testing completion
            "expected_start": None,
            "expected_end": date(2024, 3, 15),
            "expected_is_running": False,  # Past date = completed
            "description": "ASAP format with past end date (completed campaign)"
        }
    ]

    # Standard date range formats
    STANDARD_FORMATS = [
        {
            "runtime_string": "07.07.2025-24.07.2025",
            "expected_start": date(2025, 7, 7),
            "expected_end": date(2025, 7, 24),
            "expected_is_running": True,
            "description": "Standard format with July dates"
        },
        {
            "runtime_string": "01.01.2025-31.01.2025",
            "expected_start": date(2025, 1, 1),
            "expected_end": date(2025, 1, 31),
            "expected_is_running": True,
            "description": "Standard format spanning full January"
        },
        {
            "runtime_string": "15.02.2024-28.02.2024",  # Past dates
            "expected_start": date(2024, 2, 15),
            "expected_end": date(2024, 2, 28),
            "expected_is_running": False,
            "description": "Standard format with past dates (completed campaign)"
        }
    ]

    # Edge cases and malformed formats for error handling tests
    MALFORMED_FORMATS = [
        {
            "runtime_string": "ASAP-30.13.2025",  # Invalid month
            "expected_error": ValueError,
            "description": "Invalid month in ASAP format"
        },
        {
            "runtime_string": "32.01.2025-31.01.2025",  # Invalid day
            "expected_error": ValueError,
            "description": "Invalid day in standard format"
        },
        {
            "runtime_string": "07.07.2025-06.07.2025",  # End before start
            "expected_error": ValueError,
            "description": "End date before start date"
        },
        {
            "runtime_string": "ASAP",  # Missing end date
            "expected_error": ValueError,
            "description": "Incomplete ASAP format"
        },
        {
            "runtime_string": "07.07.2025-",  # Missing end date
            "expected_error": ValueError,
            "description": "Missing end date in standard format"
        },
        {
            "runtime_string": "",  # Empty string
            "expected_error": ValueError,
            "description": "Empty runtime string"
        }
    ]


class CampaignClassificationData:
    """Test data for Campaign vs Deal classification"""

    CAMPAIGNS = [
        {
            "buyer": "Not set",
            "expected_type": "campaign",
            "description": "Standard campaign with 'Not set' buyer"
        },
        {
            "buyer": "not set",  # Case sensitivity test
            "expected_type": "deal",  # Note: Only exact "Not set" = campaign
            "description": "Case sensitivity - lowercase 'not set' should be deal"
        },
        {
            "buyer": "Not Set",  # Capitalization test
            "expected_type": "deal",  # Note: Only exact "Not set" = campaign
            "description": "Case sensitivity - 'Not Set' should be deal"
        }
    ]

    DEALS = [
        {
            "buyer": "DENTSU_AEGIS < Easymedia_rtb (Seat 608194)",
            "expected_type": "deal",
            "description": "Standard deal with complex buyer string"
        },
        {
            "buyer": "AMAZON_DSP < Amazon_DSP (Seat 123456)",
            "expected_type": "deal",
            "description": "Another deal format"
        },
        {
            "buyer": "   Not set   ",  # Whitespace test
            "expected_type": "deal",  # Whitespace makes it not exact match
            "description": "Whitespace around 'Not set' should be deal"
        }
    ]


class UUIDTestData:
    """Test data for UUID validation and preservation"""

    VALID_UUIDS = [
        "56cc787c-a703-4cd3-995a-4b42eb408dfb",
        "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "00000000-0000-0000-0000-000000000000",  # All zeros valid UUID
        "ffffffff-ffff-ffff-ffff-ffffffffffff"   # All f's valid UUID
    ]

    INVALID_UUIDS = [
        "56cc787c-a703-4cd3-995a-4b42eb408df",   # Too short
        "56cc787c-a703-4cd3-995a-4b42eb408dfbx", # Too long
        "56cc787c_a703_4cd3_995a_4b42eb408dfb",  # Wrong separators
        "not-a-uuid-at-all-really-not",          # Not UUID format
        "",                                       # Empty string
        "56cc787c-a703-4cd3-995a-4b42eb408dfg"   # Invalid hex character
    ]


class DataConversionTestData:
    """Test data for XLSX data type conversion edge cases"""

    BUDGET_FORMATS = [
        {
            "input": "2396690,38",     # European decimal comma
            "expected": 2396690.38,
            "description": "Standard European format with comma decimal"
        },
        {
            "input": "1.234.567,89",   # European thousands separator
            "expected": 1234567.89,
            "description": "European format with dot thousands separator"
        },
        {
            "input": "0,00",
            "expected": 0.0,
            "description": "Zero budget"
        },
        {
            "input": "1234567.89",     # US format (should we handle this?)
            "expected": 1234567.89,
            "description": "US format with dot decimal"
        }
    ]

    IMPRESSION_GOAL_FORMATS = [
        {
            "input": "2000000000",
            "expected": 2000000000,
            "description": "Maximum impression goal (system limit)"
        },
        {
            "input": "1500000",
            "expected": 1500000,
            "description": "Standard impression goal value"
        },
        {
            "input": "1",
            "expected": 1,
            "description": "Minimum impression goal value"
        },
        {
            "input": "750000",
            "expected": 750000,
            "description": "Medium impression goal value"
        }
    ]


class ComprehensiveCampaignFixtures:
    """Complete campaign records for integration testing"""

    @staticmethod
    def get_sample_campaigns() -> List[Dict[str, Any]]:
        """
        Returns realistic campaign data combining all test scenarios.

        This data demonstrates:
        - Both ASAP and standard Runtime formats
        - Campaign vs Deal classification
        - Valid UUID formats
        - European number formatting
        - Running vs completed campaigns
        """
        return [
            {
                "name": "2025_10147_0303_1_PV Promotion | UML | GIGA | CN-Autorinnen-Ausschreibung 2025",
                "runtime": "ASAP-30.06.2025",
                "impression_goal": 2000000000,
                "budget_eur": "2396690,38",
                "cpm_eur": "1,183",
                "id": "56cc787c-a703-4cd3-995a-4b42eb408dfb",
                "buyer": "Not set",
                "expected_type": "campaign",
                "expected_is_running": True,
                "expected_start_date": None,
                "expected_end_date": date(2025, 6, 30)
            },
            {
                "name": "Summer Campaign 2025 | Fashion | Premium Inventory",
                "runtime": "07.07.2025-24.07.2025",
                "impression_goal": 1500000,
                "budget_eur": "125000,50",
                "cpm_eur": "2,45",
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "buyer": "DENTSU_AEGIS < Easymedia_rtb (Seat 608194)",
                "expected_type": "deal",
                "expected_is_running": True,
                "expected_start_date": date(2025, 7, 7),
                "expected_end_date": date(2025, 7, 24)
            },
            {
                "name": "Completed Q1 Campaign 2024 | Tech | Mobile",
                "runtime": "15.02.2024-28.02.2024",
                "impression_goal": 750000,
                "budget_eur": "45000,00",
                "cpm_eur": "0,95",
                "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
                "buyer": "Not set",
                "expected_type": "campaign",
                "expected_is_running": False,  # Past dates = completed
                "expected_start_date": date(2024, 2, 15),
                "expected_end_date": date(2024, 2, 28)
            },
            {
                "name": "Year-end ASAP Campaign | Retail | Desktop+Mobile",
                "runtime": "ASAP-31.12.2025",
                "impression_goal": 5000000,
                "budget_eur": "1.500.000,75",  # Large budget with thousands separator
                "cpm_eur": "3,25",
                "id": "c3d4e5f6-g7h8-9012-cdef-345678901234",
                "buyer": "AMAZON_DSP < Amazon_DSP (Seat 789012)",
                "expected_type": "deal",
                "expected_is_running": True,
                "expected_start_date": None,  # ASAP
                "expected_end_date": date(2025, 12, 31)
            }
        ]

    @staticmethod
    def get_malformed_campaigns() -> List[Dict[str, Any]]:
        """
        Returns campaign data with various malformation scenarios.
        Critical for testing error handling and data validation.
        """
        return [
            {
                "name": "Invalid Runtime Format Campaign",
                "runtime": "ASAP-30.13.2025",  # Invalid month
                "impression_goal": 1000000,
                "budget_eur": "50000,00",
                "cpm_eur": "2,00",
                "id": "invalid-uuid-format",  # Invalid UUID
                "buyer": "Not set",
                "expected_errors": ["runtime_parse_error", "uuid_validation_error"]
            },
            {
                "name": "Missing Critical Data Campaign",
                "runtime": "",  # Empty runtime
                "impression_goal": "",  # Empty impression goal
                "budget_eur": "invalid-budget",  # Invalid budget format
                "cpm_eur": "2,00",
                "id": "",  # Empty UUID
                "buyer": None,  # None buyer
                "expected_errors": ["runtime_required", "impression_goal_required", "budget_format_error", "uuid_required", "buyer_required"]
            }
        ]


# Pytest fixtures for easy test integration
@pytest.fixture
def runtime_test_data():
    """Provides RuntimeFormat test data for parametrized tests"""
    return RuntimeFormat()

@pytest.fixture
def classification_test_data():
    """Provides CampaignClassificationData for parametrized tests"""
    return CampaignClassificationData()

@pytest.fixture
def uuid_test_data():
    """Provides UUIDTestData for validation tests"""
    return UUIDTestData()

@pytest.fixture
def conversion_test_data():
    """Provides DataConversionTestData for format conversion tests"""
    return DataConversionTestData()

@pytest.fixture
def sample_campaigns():
    """Provides complete campaign fixtures for integration tests"""
    return ComprehensiveCampaignFixtures.get_sample_campaigns()

@pytest.fixture
def malformed_campaigns():
    """Provides malformed campaign data for error handling tests"""
    return ComprehensiveCampaignFixtures.get_malformed_campaigns()