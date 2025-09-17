"""
Runtime Parser Service TDD Template - Discovery-Driven Testing

This template demonstrates:
1. Hypothesis-driven test design for unknown parsing requirements
2. Safe experimentation with evolutionary test patterns
3. Learning documentation through test evolution
4. Red-Green-Refactor cycle adapted for discovery projects

Educational Focus: Shows backend-engineer exactly how to implement TDD
for discovery-driven development where requirements emerge through iteration.
"""

import pytest
from datetime import date
from typing import Optional, Dict, Any

# Import your fixtures
from ..fixtures.campaign_test_data import RuntimeFormat

# Mock imports - backend-engineer will replace with actual service imports
# from app.services.runtime_parser import RuntimeParser, ParseResult
# from app.exceptions import RuntimeParseError


class MockParseResult:
    """Mock result class - backend-engineer will replace with actual implementation"""
    def __init__(self, start_date: Optional[date], end_date: date, is_running: bool = True):
        self.start_date = start_date
        self.end_date = end_date
        self.is_running = is_running


class MockRuntimeParser:
    """Mock parser - backend-engineer will replace with actual implementation"""
    def parse(self, runtime_string: str) -> MockParseResult:
        # This is where the actual parsing logic will go
        # For now, just raise NotImplementedError to demonstrate Red phase
        raise NotImplementedError("RuntimeParser.parse() not yet implemented")


# =============================================================================
# DISCOVERY TDD PATTERN 1: Hypothesis-Driven Test Design
# =============================================================================

@pytest.mark.runtime_parsing
class TestRuntimeParserDiscovery:
    """
    Discovery TDD Approach: Test hypotheses about runtime parsing behavior

    Instead of testing known requirements, we test our hypotheses about
    how the system should handle various runtime formats we've discovered.
    """

    def setup_method(self):
        """Setup for each test - backend-engineer will inject real service"""
        self.parser = MockRuntimeParser()

    @pytest.mark.parametrize("test_case", RuntimeFormat.ASAP_FORMATS)
    def test_asap_format_hypothesis(self, test_case):
        """
        HYPOTHESIS: ASAP-DD.MM.YYYY format should parse with None start_date

        Discovery Question: How do we handle undefined start dates?
        Business Context: ASAP campaigns start "as soon as possible"

        This test documents our learning about ASAP format behavior.
        """
        # ARRANGE - Use our excellent test fixtures
        runtime_string = test_case["runtime_string"]
        expected_start = test_case["expected_start"]  # Should be None for ASAP
        expected_end = test_case["expected_end"]

        # ACT - This will fail initially (Red phase)
        with pytest.raises(NotImplementedError):
            result = self.parser.parse(runtime_string)

        # This is what we expect after implementation (Green phase):
        # result = self.parser.parse(runtime_string)

        # ASSERT - Document expected behavior for backend-engineer
        # assert result.start_date == expected_start
        # assert result.end_date == expected_end
        # assert isinstance(result.end_date, date)

        # Learning Documentation: ASAP means start_date = None
        print(f"Learning: {test_case['description']} - start should be {expected_start}")

    @pytest.mark.parametrize("test_case", RuntimeFormat.STANDARD_FORMATS)
    def test_standard_format_hypothesis(self, test_case):
        """
        HYPOTHESIS: DD.MM.YYYY-DD.MM.YYYY format should parse both dates

        Discovery Question: How do we handle date range parsing?
        Business Context: Standard campaigns have defined start and end

        This test evolves as we learn about date range complexity.
        """
        # ARRANGE
        runtime_string = test_case["runtime_string"]
        expected_start = test_case["expected_start"]
        expected_end = test_case["expected_end"]

        # ACT - Red phase: will fail until implemented
        with pytest.raises(NotImplementedError):
            result = self.parser.parse(runtime_string)

        # Expected after implementation:
        # result = self.parser.parse(runtime_string)

        # ASSERT - Both dates should be parsed
        # assert result.start_date == expected_start
        # assert result.end_date == expected_end
        # assert result.start_date is not None  # Unlike ASAP format

        print(f"Learning: {test_case['description']} - both dates defined")


# =============================================================================
# DISCOVERY TDD PATTERN 2: Error Handling Through Hypothesis Testing
# =============================================================================

@pytest.mark.runtime_parsing
class TestRuntimeParserErrorDiscovery:
    """
    Discovery TDD: Test our hypotheses about error conditions

    We don't know all the ways parsing can fail, so we test scenarios
    we've discovered and document what we learn.
    """

    def setup_method(self):
        self.parser = MockRuntimeParser()

    @pytest.mark.parametrize("test_case", RuntimeFormat.MALFORMED_FORMATS)
    def test_malformed_format_error_handling(self, test_case):
        """
        HYPOTHESIS: Malformed runtime strings should raise specific errors

        Discovery Pattern: Test edge cases to understand system boundaries
        Learning Goal: Document what constitutes valid vs invalid formats
        """
        # ARRANGE
        runtime_string = test_case["runtime_string"]
        expected_error = test_case["expected_error"]

        # ACT & ASSERT - Test error hypothesis
        with pytest.raises(expected_error):
            # This will initially raise NotImplementedError (Red phase)
            # Backend-engineer will implement proper error handling (Green phase)
            result = self.parser.parse(runtime_string)

        # Learning Documentation
        print(f"Learning: {test_case['description']} should raise {expected_error.__name__}")

    def test_empty_string_handling_discovery(self):
        """
        DISCOVERY TEST: How should we handle empty runtime strings?

        This test documents a specific edge case we discovered.
        As we learn more, this test might evolve.
        """
        # HYPOTHESIS: Empty string should raise ValueError
        with pytest.raises(ValueError):
            self.parser.parse("")

        # Alternative hypothesis to explore:
        # Should empty string return None? Or default dates?
        # This test can evolve as requirements become clearer


# =============================================================================
# DISCOVERY TDD PATTERN 3: Business Logic Discovery Through Testing
# =============================================================================

@pytest.mark.runtime_parsing
@pytest.mark.completion_validation
class TestCampaignCompletionDiscovery:
    """
    Discovery TDD: Explore business rules through hypothesis testing

    We're discovering how campaign completion should work by testing
    different scenarios against current date.
    """

    def setup_method(self):
        self.parser = MockRuntimeParser()

    def test_completion_logic_hypothesis(self, mock_current_date):
        """
        HYPOTHESIS: Campaigns are completed when end_date <= current_date

        Discovery Question: How do we determine if a campaign is running?
        Business Rule Discovery: What happens at the date boundary?
        """
        # ARRANGE - Test boundary conditions
        test_scenarios = [
            {
                "current_date": date(2025, 6, 30),
                "runtime": "ASAP-30.06.2025",  # Ends today
                "expected_is_running": False,  # Hypothesis: ends today = completed
                "description": "Campaign ending today should be completed"
            },
            {
                "current_date": date(2025, 6, 29),
                "runtime": "ASAP-30.06.2025",  # Ends tomorrow
                "expected_is_running": True,   # Hypothesis: ends tomorrow = running
                "description": "Campaign ending tomorrow should be running"
            }
        ]

        for scenario in test_scenarios:
            with mock_current_date(scenario["current_date"]):
                # ACT - Red phase: will fail until logic implemented
                with pytest.raises(NotImplementedError):
                    result = self.parser.parse(scenario["runtime"])

                # Expected after implementation:
                # result = self.parser.parse(scenario["runtime"])
                # assert result.is_running == scenario["expected_is_running"]

                print(f"Learning: {scenario['description']}")


# =============================================================================
# DISCOVERY TDD PATTERN 4: Integration Discovery Testing
# =============================================================================

@pytest.mark.runtime_parsing
@pytest.mark.integration
class TestRuntimeParserIntegrationDiscovery:
    """
    Discovery TDD: Test integration scenarios to understand system behavior

    These tests explore how runtime parsing integrates with other components.
    """

    def test_campaign_data_integration_hypothesis(self, sample_campaigns):
        """
        HYPOTHESIS: Parser should handle all campaign formats from real data

        Discovery Pattern: Test against realistic data combinations
        Learning Goal: Ensure parser works with complete campaign records
        """
        parser = MockRuntimeParser()

        # Test all campaign formats we discovered in our fixtures
        for campaign in sample_campaigns:
            runtime_string = campaign["runtime"]
            expected_start = campaign["expected_start_date"]
            expected_end = campaign["expected_end_date"]

            # Red phase: will fail until implemented
            with pytest.raises(NotImplementedError):
                result = parser.parse(runtime_string)

            # Expected behavior after implementation:
            # result = parser.parse(runtime_string)
            # assert result.start_date == expected_start
            # assert result.end_date == expected_end

            print(f"Learning: Successfully parsed {campaign['name']}")


# =============================================================================
# TDD GUIDANCE FOR BACKEND-ENGINEER
# =============================================================================

"""
IMPLEMENTATION GUIDANCE FOR BACKEND-ENGINEER:

1. RED PHASE (Current State):
   - All tests fail with NotImplementedError
   - This is expected and correct for TDD

2. GREEN PHASE (Next Steps):
   - Implement RuntimeParser.parse() method
   - Make tests pass with minimal code
   - Focus on making one test green at a time

3. REFACTOR PHASE:
   - Improve code quality while keeping tests green
   - Extract parsing logic into helper methods
   - Add performance optimizations

DISCOVERY TDD APPROACH:
- Start with ASAP format tests (simpler case)
- Then implement standard format parsing
- Add error handling for malformed formats
- Finally implement completion logic

EXAMPLE IMPLEMENTATION SKELETON:

class RuntimeParser:
    def parse(self, runtime_string: str) -> ParseResult:
        if not runtime_string:
            raise ValueError("Runtime string cannot be empty")

        if runtime_string.startswith("ASAP-"):
            return self._parse_asap_format(runtime_string)
        elif "-" in runtime_string:
            return self._parse_standard_format(runtime_string)
        else:
            raise ValueError(f"Invalid runtime format: {runtime_string}")

    def _parse_asap_format(self, runtime_string: str) -> ParseResult:
        # Extract end date, start_date = None
        pass

    def _parse_standard_format(self, runtime_string: str) -> ParseResult:
        # Extract both start and end dates
        pass

TESTING APPROACH:
- Run: pytest tests/test_services/test_runtime_parser.py -v
- Watch tests fail (Red)
- Implement minimal code to make them pass (Green)
- Refactor while keeping tests green (Refactor)
"""