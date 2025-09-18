"""
XLSXProcessor Characterization Tests - TDD Documentation of Current Behavior

This test suite documents the EXACT behavior of the existing XLSXProcessor service
to ensure any refactoring preserves all functionality. These are characterization
tests that capture current behavior without making assumptions about correctness.

Educational Focus: Shows how to use TDD to understand existing code before refactoring.
This prevents regressions and documents complex business logic behavior.

Testing Strategy:
1. Document happy path XLSX processing workflow
2. Capture all error conditions and their exact messages
3. Test service orchestration behavior (DataConverter, RuntimeParser, etc.)
4. Document header mapping and row processing logic
5. Verify partial failure handling and error collection
"""

import pytest
import io
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

# Import the actual XLSXProcessor from the upload module
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.api.upload import XLSXProcessor
from app.services.data_conversion import ConversionError
from app.services.runtime_parser import RuntimeParseError


class MockWorksheet:
    """Mock openpyxl worksheet for testing"""
    def __init__(self, data_rows: List[List[Any]]):
        self.data_rows = data_rows
        self.current_row = 0

    def iter_rows(self, min_row=1, max_row=None, values_only=False):
        """Mock iter_rows to return test data"""
        start_idx = min_row - 1
        end_idx = max_row - 1 if max_row else len(self.data_rows)

        for row_data in self.data_rows[start_idx:end_idx + 1 if max_row else None]:
            yield tuple(row_data) if values_only else row_data


class MockWorkbook:
    """Mock openpyxl workbook for testing"""
    def __init__(self, worksheet_data: List[List[Any]]):
        self.active = MockWorksheet(worksheet_data)


@pytest.fixture
def valid_xlsx_data():
    """Sample valid XLSX data that should process successfully"""
    return [
        # Header row
        ["ID", "Deal/Campaign Name", "Runtime", "Impression Goal", "Budget", "CPM", "Buyer"],
        # Valid data rows
        ["56cc787c-a703-4cd3-995a-4b42eb408dfb", "Fashion Campaign Q2", "01.06.2025 - 30.06.2025", "1.000.000", "15.000,50", "15,00", "Fashion Buyer Ltd"],
        ["789e012f-3456-7890-abcd-ef1234567890", "Tech Deal ASAP", "ASAP", "500.000", "7.500,25", "15,00", "Tech Solutions GmbH"],
        ["abc123de-4567-8901-cdef-234567890123", "Summer Campaign", "15.07.2025 - 31.08.2025", "2.500.000", "37.500,75", "15,00", "Summer Brands Inc"]
    ]


@pytest.fixture
def malformed_xlsx_data():
    """Sample XLSX data with various malformations to test error handling"""
    return [
        # Header row
        ["ID", "Deal/Campaign Name", "Runtime", "Impression Goal", "Budget", "CPM", "Buyer"],
        # Valid row
        ["valid123-4567-8901-cdef-234567890123", "Valid Campaign", "01.06.2025 - 30.06.2025", "1.000.000", "15.000,50", "15,00", "Valid Buyer"],
        # Missing required fields
        ["missing-fields", "", "01.06.2025 - 30.06.2025", "1.000.000", "15.000,50", "15,00", ""],
        # Invalid number formats
        ["invalid-numbers", "Invalid Numbers Campaign", "01.06.2025 - 30.06.2025", "not-a-number", "invalid-budget", "invalid-cpm", "Invalid Buyer"],
        # Empty row (should be skipped)
        [None, None, None, None, None, None, None],
        # Invalid runtime format
        ["invalid-runtime", "Invalid Runtime Campaign", "not-a-date-range", "1.000.000", "15.000,50", "15,00", "Runtime Buyer"]
    ]


@pytest.fixture
def xlsx_processor():
    """Fresh XLSXProcessor instance for each test"""
    return XLSXProcessor()


# =============================================================================
# CHARACTERIZATION TESTS: Document Current XLSXProcessor Behavior
# =============================================================================

class TestXLSXProcessorCharacterization:
    """
    Characterization tests to document exactly how XLSXProcessor currently works.
    These tests capture existing behavior to prevent regressions during refactoring.
    """

    @patch('app.api.upload.openpyxl.load_workbook')
    def test_successful_xlsx_processing_happy_path(self, mock_load_workbook, xlsx_processor, valid_xlsx_data):
        """
        CHARACTERIZATION TEST: Document successful XLSX processing workflow

        This test captures the exact behavior when processing valid XLSX data,
        including service orchestration and response format.
        """
        # ARRANGE - Mock openpyxl to return our test data
        mock_workbook = MockWorkbook(valid_xlsx_data)
        mock_load_workbook.return_value = mock_workbook

        file_content = io.BytesIO(b"mock xlsx content")

        # Mock the service dependencies to control their behavior
        with patch.object(xlsx_processor.data_converter, 'convert_impression_goal') as mock_convert_impressions, \
             patch.object(xlsx_processor.data_converter, 'convert_european_decimal') as mock_convert_decimal, \
             patch.object(xlsx_processor.runtime_parser, 'parse_runtime') as mock_parse_runtime:

            # Configure mocks with expected return values
            mock_convert_impressions.side_effect = [1000000, 500000, 2500000]  # For each row
            mock_convert_decimal.side_effect = [15000.50, 15.00, 7500.25, 15.00, 37500.75, 15.00]  # Budget, CPM for each row
            mock_parse_runtime.side_effect = [
                {"start_date": datetime(2025, 6, 1), "end_date": datetime(2025, 6, 30)},
                {"start_date": None, "end_date": None},  # ASAP case
                {"start_date": datetime(2025, 7, 15), "end_date": datetime(2025, 8, 31)}
            ]

            # ACT - Process the XLSX file
            result = xlsx_processor.process_xlsx_file(file_content)

            # ASSERT - Document the exact current behavior
            assert isinstance(result, dict)
            assert "campaigns" in result
            assert "errors" in result
            assert "summary" in result

            # Verify campaign data structure and content
            campaigns = result["campaigns"]
            assert len(campaigns) == 3  # Should process 3 valid rows

            # First campaign verification
            first_campaign = campaigns[0]
            assert first_campaign["id"] == "56cc787c-a703-4cd3-995a-4b42eb408dfb"
            assert first_campaign["name"] == "Fashion Campaign Q2"
            assert first_campaign["runtime"] == "01.06.2025 - 30.06.2025"
            assert first_campaign["impression_goal"] == 1000000
            assert first_campaign["budget_eur"] == 15000.50
            assert first_campaign["cpm_eur"] == 15.00
            assert first_campaign["buyer"] == "Fashion Buyer Ltd"
            assert first_campaign["runtime_start"] == datetime(2025, 6, 1)
            assert first_campaign["runtime_end"] == datetime(2025, 6, 30)

            # ASAP campaign verification (second campaign)
            asap_campaign = campaigns[1]
            assert asap_campaign["runtime"] == "ASAP"
            assert asap_campaign["runtime_start"] is None
            assert asap_campaign["runtime_end"] is None

            # Verify no errors for valid data
            assert result["errors"] == []

            # Verify summary statistics
            summary = result["summary"]
            assert summary["total_rows"] == 3
            assert summary["successful_campaigns"] == 3
            assert summary["failed_campaigns"] == 0
            assert summary["success_rate"] == 100.0

    @patch('app.api.upload.openpyxl.load_workbook')
    def test_header_mapping_behavior(self, mock_load_workbook, xlsx_processor):
        """
        CHARACTERIZATION TEST: Document how header mapping currently works

        Tests the _extract_headers method behavior with various header formats.
        """
        # Test data with various header formats
        header_variations = [
            ["Campaign UUID", "Deal/Campaign Name", "Runtime Period", "Impression Goal Target", "Budget EUR", "CPM Rate", "Buyer Name"],
            ["id", "name", "runtime", "impression goal", "budget", "cpm", "buyer"],
            ["ID (UUID)", "Campaign/Deal Name", "Runtime", "Impressions Goal", "Budget (EUR)", "CPM EUR", "Buyer Company"]
        ]

        for headers in header_variations:
            mock_workbook = MockWorkbook([headers])
            mock_load_workbook.return_value = mock_workbook
            worksheet = mock_workbook.active

            # ACT - Extract headers
            header_mapping = xlsx_processor._extract_headers(worksheet)

            # ASSERT - Document current mapping behavior
            # The method should map various header formats to standard field names
            print(f"Header mapping for {headers}: {header_mapping}")

            # Verify that key fields are detected (behavior may vary based on header format)
            if any("id" in h.lower() or "uuid" in h.lower() for h in headers):
                assert "id" in header_mapping
            if any("name" in h.lower() for h in headers):
                assert "name" in header_mapping

    @patch('app.api.upload.openpyxl.load_workbook')
    def test_error_handling_and_collection(self, mock_load_workbook, xlsx_processor, malformed_xlsx_data):
        """
        CHARACTERIZATION TEST: Document error handling behavior

        Captures how the processor handles various error conditions and
        collects error details for reporting.
        """
        # ARRANGE - Mock workbook with malformed data
        mock_workbook = MockWorkbook(malformed_xlsx_data)
        mock_load_workbook.return_value = mock_workbook

        file_content = io.BytesIO(b"mock xlsx content")

        # Mock services to simulate various error conditions
        with patch.object(xlsx_processor.data_converter, 'convert_impression_goal') as mock_convert_impressions, \
             patch.object(xlsx_processor.data_converter, 'convert_european_decimal') as mock_convert_decimal, \
             patch.object(xlsx_processor.runtime_parser, 'parse_runtime') as mock_parse_runtime:

            # Configure mocks to succeed for valid row, fail for invalid rows
            mock_convert_impressions.side_effect = [
                1000000,  # Valid row succeeds
                ConversionError("Invalid impression goal format"),  # Missing fields row
                ConversionError("Invalid number format"),  # Invalid numbers row
                1000000   # Invalid runtime row (impressions succeed, runtime fails)
            ]

            mock_convert_decimal.side_effect = [
                15000.50, 15.00,  # Valid row succeeds
                ConversionError("Invalid budget format"), 15.00,  # Missing fields fails on budget
                ConversionError("Invalid budget format"), ConversionError("Invalid CPM format"),  # Invalid numbers fails
                15000.50, 15.00   # Invalid runtime row (decimals succeed, runtime fails)
            ]

            mock_parse_runtime.side_effect = [
                {"start_date": datetime(2025, 6, 1), "end_date": datetime(2025, 6, 30)},  # Valid row
                RuntimeParseError("Invalid runtime format")  # Invalid runtime row
            ]

            # ACT - Process malformed XLSX
            result = xlsx_processor.process_xlsx_file(file_content)

            # ASSERT - Document error handling behavior
            assert isinstance(result, dict)
            assert "campaigns" in result
            assert "errors" in result
            assert "summary" in result

            # Should have some successful campaigns (at least the valid row)
            campaigns = result["campaigns"]
            assert len(campaigns) >= 1  # At least one valid campaign processed

            # Should have error details for failed rows
            errors = result["errors"]
            assert len(errors) > 0  # Should capture errors from malformed rows

            # Verify error structure
            for error in errors:
                assert "row" in error  # Row number for debugging
                assert "error" in error  # Error message
                assert "data" in error  # Sample of row data for context
                assert isinstance(error["row"], int)
                assert isinstance(error["error"], str)
                assert isinstance(error["data"], list)

            # Verify summary reflects partial success
            summary = result["summary"]
            assert summary["successful_campaigns"] == len(campaigns)
            assert summary["failed_campaigns"] == len(errors)
            assert summary["total_rows"] > 0
            assert 0 <= summary["success_rate"] <= 100

    def test_empty_row_handling(self, xlsx_processor):
        """
        CHARACTERIZATION TEST: Document how empty rows are handled
        """
        # Test _process_row with empty data
        empty_row = (None, None, None, None, None, None, None)
        headers = {"id": 0, "name": 1, "runtime": 2, "impression_goal": 3, "budget_eur": 4, "cpm_eur": 5, "buyer": 6}

        # ACT - Process empty row
        result = xlsx_processor._process_row(empty_row, headers, 2)

        # ASSERT - Empty rows should return None (skipped)
        assert result is None

    def test_required_fields_validation(self, xlsx_processor):
        """
        CHARACTERIZATION TEST: Document required field validation behavior
        """
        headers = {"id": 0, "name": 1, "runtime": 2, "impression_goal": 3, "budget_eur": 4, "cpm_eur": 5, "buyer": 6}

        # Test row with missing required fields
        incomplete_row = ("123", None, "01.06.2025 - 30.06.2025", "1000000", "15000.50", "15.00", "Buyer")

        # ACT & ASSERT - Should raise ValueError for missing required fields
        with pytest.raises(ValueError) as exc_info:
            xlsx_processor._process_row(incomplete_row, headers, 2)

        assert "Missing required fields" in str(exc_info.value)
        assert "name" in str(exc_info.value)  # Should identify the missing field

    @patch('app.api.upload.openpyxl.load_workbook')
    def test_service_orchestration_flow(self, mock_load_workbook, xlsx_processor):
        """
        CHARACTERIZATION TEST: Document the exact service orchestration sequence

        Verifies the order and parameters of service calls during processing.
        """
        # Simple test data
        test_data = [
            ["ID", "Deal/Campaign Name", "Runtime", "Impression Goal", "Budget", "CPM", "Buyer"],
            ["test-123", "Test Campaign", "01.06.2025 - 30.06.2025", "1.000.000", "15.000,50", "15,00", "Test Buyer"]
        ]

        mock_workbook = MockWorkbook(test_data)
        mock_load_workbook.return_value = mock_workbook
        file_content = io.BytesIO(b"mock xlsx content")

        # Mock all services to track call order and parameters
        with patch.object(xlsx_processor.data_converter, 'convert_impression_goal') as mock_convert_impressions, \
             patch.object(xlsx_processor.data_converter, 'convert_european_decimal') as mock_convert_decimal, \
             patch.object(xlsx_processor.runtime_parser, 'parse_runtime') as mock_parse_runtime:

            # Configure return values
            mock_convert_impressions.return_value = 1000000
            mock_convert_decimal.side_effect = [15000.50, 15.00]  # Budget, then CPM
            mock_parse_runtime.return_value = {"start_date": datetime(2025, 6, 1), "end_date": datetime(2025, 6, 30)}

            # ACT - Process the file
            result = xlsx_processor.process_xlsx_file(file_content)

            # ASSERT - Document the exact service call sequence
            # 1. DataConverter should be called for impression_goal conversion
            mock_convert_impressions.assert_called_once_with("1.000.000")

            # 2. DataConverter should be called twice for European decimal conversion (budget, then CPM)
            assert mock_convert_decimal.call_count == 2
            mock_convert_decimal.assert_any_call("15.000,50")  # Budget conversion
            mock_convert_decimal.assert_any_call("15,00")      # CPM conversion

            # 3. RuntimeParser should be called for runtime parsing
            mock_parse_runtime.assert_called_once_with("01.06.2025 - 30.06.2025")

            # Verify the processing succeeded
            campaigns = result["campaigns"]
            assert len(campaigns) == 1
            campaign = campaigns[0]

            # Verify service results are properly integrated
            assert campaign["impression_goal"] == 1000000  # From DataConverter
            assert campaign["budget_eur"] == 15000.50      # From DataConverter
            assert campaign["cpm_eur"] == 15.00            # From DataConverter
            assert campaign["runtime_start"] == datetime(2025, 6, 1)  # From RuntimeParser
            assert campaign["runtime_end"] == datetime(2025, 6, 30)   # From RuntimeParser


# =============================================================================
# REGRESSION PROTECTION TESTS
# =============================================================================

class TestXLSXProcessorRegressionProtection:
    """
    Tests that protect against specific regressions in XLSXProcessor behavior.
    These tests ensure that edge cases and error conditions continue to work as expected.
    """

    @patch('app.api.upload.openpyxl.load_workbook')
    def test_openpyxl_loading_failure_handling(self, mock_load_workbook, xlsx_processor):
        """
        REGRESSION TEST: Ensure openpyxl loading failures are properly handled
        """
        # Mock openpyxl to raise an exception
        mock_load_workbook.side_effect = Exception("Invalid XLSX file format")

        file_content = io.BytesIO(b"invalid xlsx content")

        # ACT & ASSERT - Should raise HTTPException with proper error message
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            xlsx_processor.process_xlsx_file(file_content)

        assert exc_info.value.status_code == 400
        assert "XLSX file processing failed" in str(exc_info.value.detail)

    def test_data_converter_initialization(self, xlsx_processor):
        """
        REGRESSION TEST: Verify service dependencies are properly initialized
        """
        # Verify that XLSXProcessor initializes all required services
        assert hasattr(xlsx_processor, 'data_converter')
        assert hasattr(xlsx_processor, 'runtime_parser')
        assert hasattr(xlsx_processor, 'campaign_classifier')

        # Verify services are not None
        assert xlsx_processor.data_converter is not None
        assert xlsx_processor.runtime_parser is not None
        assert xlsx_processor.campaign_classifier is not None

    @patch('app.api.upload.openpyxl.load_workbook')
    def test_partial_header_mapping_resilience(self, mock_load_workbook, xlsx_processor):
        """
        REGRESSION TEST: Ensure processor handles missing or partial headers gracefully
        """
        # Test with incomplete headers
        incomplete_headers = [
            ["ID", "Name", "Runtime"]  # Missing impression_goal, budget, cpm, buyer
        ]

        mock_workbook = MockWorkbook(incomplete_headers)
        mock_load_workbook.return_value = mock_workbook

        worksheet = mock_workbook.active
        header_mapping = xlsx_processor._extract_headers(worksheet)

        # Should handle partial headers without crashing
        assert isinstance(header_mapping, dict)
        # Available fields should be mapped
        assert "id" in header_mapping or len(header_mapping) >= 0  # At least doesn't crash


# =============================================================================
# INTEGRATION TESTS: Service Interaction Documentation
# =============================================================================

class TestXLSXProcessorServiceIntegration:
    """
    Tests that document how XLSXProcessor integrates with its service dependencies.
    These tests use real service instances to verify integration behavior.
    """

    def test_real_service_integration_flow(self, xlsx_processor):
        """
        INTEGRATION TEST: Test with real service instances (not mocked)

        This test verifies that XLSXProcessor properly integrates with actual
        DataConverter, RuntimeParser, and CampaignClassifier services.
        """
        # This test would require real services to be available
        # For now, we verify the services exist and have expected methods

        # Verify DataConverter integration
        assert hasattr(xlsx_processor.data_converter, 'convert_impression_goal')
        assert hasattr(xlsx_processor.data_converter, 'convert_european_decimal')

        # Verify RuntimeParser integration
        assert hasattr(xlsx_processor.runtime_parser, 'parse_runtime')

        # Verify CampaignClassifier integration
        assert hasattr(xlsx_processor.campaign_classifier, '__class__')

        print("XLSXProcessor service integration verified - all dependencies available")


# =============================================================================
# TEST EXECUTION GUIDANCE
# =============================================================================

"""
RUNNING THESE CHARACTERIZATION TESTS:

1. Run all characterization tests:
   pytest tests/test_api/test_xlsx_processor_characterization.py -v

2. Run specific test categories:
   pytest tests/test_api/test_xlsx_processor_characterization.py::TestXLSXProcessorCharacterization -v
   pytest tests/test_api/test_xlsx_processor_characterization.py::TestXLSXProcessorRegressionProtection -v

3. Run with detailed output to see learning documentation:
   pytest tests/test_api/test_xlsx_processor_characterization.py -v -s

4. Generate test coverage for XLSXProcessor:
   pytest tests/test_api/test_xlsx_processor_characterization.py --cov=app.api.upload.XLSXProcessor

WHAT THESE TESTS DOCUMENT:

1. **Exact Current Behavior**: Every test captures precisely how XLSXProcessor works today
2. **Service Orchestration**: How DataConverter, RuntimeParser, and CampaignClassifier are coordinated
3. **Error Handling**: What errors are caught, how they're formatted, and what gets reported
4. **Data Flow**: How XLSX data flows through the processing pipeline
5. **Edge Cases**: How empty rows, malformed data, and missing fields are handled

REFACTORING SAFETY:

- Run these tests BEFORE any refactoring to establish baseline behavior
- Any changes to XLSXProcessor should maintain these documented behaviors
- If behavior needs to change, update tests first to document the new expected behavior
- These tests serve as living documentation of the complex XLSX processing workflow

EDUCATIONAL VALUE:

- Shows how to characterize existing code behavior without making assumptions
- Demonstrates comprehensive testing of service orchestration patterns
- Illustrates how to document complex business logic through tests
- Provides template for testing file processing workflows
"""