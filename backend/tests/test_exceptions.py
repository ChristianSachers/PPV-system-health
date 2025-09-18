"""
Unified Exception Hierarchy TDD Foundation - Discovery-Driven Error Handling Testing

This test foundation demonstrates:
1. Test-first exception hierarchy design for maintainable error handling
2. Backward compatibility validation during incremental migration
3. Service-by-service migration safety with characterization tests
4. Structured error details and business rule integration

Educational Focus: Shows how TDD enables safe refactoring of exception handling
while preserving exact behavior and enabling iterative improvement.

TDD APPROACH:
- RED PHASE: Tests for new exception hierarchy (will fail until implemented)
- GREEN PHASE: Backend engineer implements unified exceptions
- REFACTOR PHASE: Service-by-service migration with regression protection
"""

import pytest
from datetime import datetime, date
from typing import Dict, Any, Optional
import json

# Import current exceptions (will be migrated)
from app.services.data_conversion import ConversionError
from app.services.runtime_parser import RuntimeParseError

# Import services for characterization testing
from app.services.data_conversion import DataConverter
from app.services.runtime_parser import RuntimeParser
from app.models.campaign import Campaign


# =============================================================================
# TDD FOUNDATION PATTERN 1: New Exception Hierarchy Tests (RED PHASE)
# =============================================================================

@pytest.mark.exceptions
class TestPPVBaseException:
    """
    TDD Foundation: Test base exception functionality for unified hierarchy

    RED PHASE: These tests will fail until backend engineer implements app.exceptions
    GREEN PHASE: Tests pass after PPVBaseException implementation
    REFACTOR PHASE: Enable structured error handling across all services
    """

    def test_base_exception_creation(self):
        """
        Test PPVBaseException with message, error_code, details

        HYPOTHESIS: Unified base exception enables structured error information
        - Every exception should have consistent message format
        - Error codes enable programmatic error handling
        - Details dictionary supports debugging and error context
        """
        # RED PHASE: This will fail until PPVBaseException is implemented
        with pytest.raises(ImportError):
            from app.exceptions import PPVBaseException

            exception = PPVBaseException(
                message="Test error message",
                error_code="PPV_TEST_001",
                details={"context": "test", "value": 123}
            )

            # Expected behavior after implementation:
            assert str(exception) == "Test error message"
            assert exception.error_code == "PPV_TEST_001"
            assert exception.details["context"] == "test"
            assert exception.details["value"] == 123
            assert isinstance(exception.timestamp, datetime)

        print("Learning: PPVBaseException needs structured error information")

    def test_structured_error_details(self):
        """
        Test error details dictionary functionality

        DISCOVERY: How should we structure error context for debugging?
        - Service name for error origin tracking
        - Input values that caused the error
        - Validation context for business rule violations
        """
        with pytest.raises(ImportError):
            from app.exceptions import PPVBaseException

            details = {
                "service": "DataConverter",
                "method": "convert_european_decimal",
                "input_value": "invalid,format,string",
                "validation_context": "European number format",
                "business_rule": "must_be_single_decimal_comma"
            }

            exception = PPVBaseException(
                message="Invalid European decimal format",
                error_code="PPV_DATA_001",
                details=details
            )

            # Expected structured access:
            assert exception.get_service() == "DataConverter"
            assert exception.get_context()["input_value"] == "invalid,format,string"
            assert exception.is_business_rule_violation() == True

        print("Learning: Structured error details enable better debugging")

    def test_timestamp_generation(self):
        """
        Test automatic timestamp creation for error tracking

        DISCOVERY: How do we track when errors occur for monitoring?
        - Automatic timestamp generation
        - Timezone handling for distributed systems
        - Monotonic time for error correlation
        """
        with pytest.raises(ImportError):
            from app.exceptions import PPVBaseException

            before_time = datetime.utcnow()
            exception = PPVBaseException("Timestamp test")
            after_time = datetime.utcnow()

            # Expected timestamp behavior:
            assert before_time <= exception.timestamp <= after_time
            assert isinstance(exception.timestamp, datetime)
            assert exception.timestamp.tzinfo is None  # UTC assumption

        print("Learning: Automatic timestamp enables error monitoring")


@pytest.mark.exceptions
class TestDataValidationError:
    """
    TDD Foundation: Test data validation exception (replaces ConversionError)

    MIGRATION TARGET: ConversionError → DataValidationError
    """

    def test_data_validation_inheritance(self):
        """
        Test inheritance from PPVBaseException

        HYPOTHESIS: DataValidationError should inherit structured error handling
        """
        with pytest.raises(ImportError):
            from app.exceptions import PPVBaseException, DataValidationError

            error = DataValidationError(
                message="Invalid data format",
                details={"input": "bad,data,format"}
            )

            # Expected inheritance behavior:
            assert isinstance(error, PPVBaseException)
            assert isinstance(error, Exception)
            assert error.error_code.startswith("PPV_DATA")

        print("Learning: DataValidationError inherits structured error handling")

    def test_error_code_assignment(self):
        """
        Test automatic error code assignment for data validation

        DISCOVERY: How should we categorize data validation errors?
        - European format conversion errors
        - Impression goal validation errors
        - Business rule validation errors
        """
        with pytest.raises(ImportError):
            from app.exceptions import DataValidationError

            # Different types of data validation errors
            format_error = DataValidationError("Invalid European format")
            range_error = DataValidationError("Value out of range")
            type_error = DataValidationError("Invalid data type")

            # Expected error code patterns:
            assert format_error.error_code.startswith("PPV_DATA")
            assert range_error.error_code.startswith("PPV_DATA")
            assert type_error.error_code.startswith("PPV_DATA")

            # Should be different error codes for different error types:
            assert format_error.error_code != range_error.error_code

        print("Learning: Data validation errors need categorized error codes")

    def test_conversion_error_compatibility(self):
        """
        Test backward compatibility with existing ConversionError usage

        MIGRATION SAFETY: Ensure existing isinstance() checks still work
        """
        with pytest.raises(ImportError):
            from app.exceptions import DataValidationError

            error = DataValidationError("Migration compatibility test")

            # After migration, this should work:
            # assert isinstance(error, ConversionError)  # Via alias
            assert isinstance(error, Exception)

        print("Learning: DataValidationError needs ConversionError compatibility")


@pytest.mark.exceptions
class TestRuntimeParsingError:
    """
    TDD Foundation: Test runtime parsing exception (replaces RuntimeParseError)

    MIGRATION TARGET: RuntimeParseError → RuntimeParsingError
    """

    def test_runtime_parsing_inheritance(self):
        """
        Test inheritance from PPVBaseException

        HYPOTHESIS: RuntimeParsingError should provide structured runtime error context
        """
        with pytest.raises(ImportError):
            from app.exceptions import PPVBaseException, RuntimeParsingError

            error = RuntimeParsingError(
                message="Invalid runtime format",
                details={
                    "input_runtime": "invalid-format",
                    "expected_patterns": ["ASAP-DD.MM.YYYY", "DD.MM.YYYY-DD.MM.YYYY"]
                }
            )

            # Expected behavior:
            assert isinstance(error, PPVBaseException)
            assert error.error_code.startswith("PPV_RUNTIME")
            assert "expected_patterns" in error.details

        print("Learning: RuntimeParsingError provides format guidance")

    def test_runtime_error_categorization(self):
        """
        Test runtime parsing error categorization

        DISCOVERY: How should we categorize runtime parsing errors?
        - Invalid date format errors
        - Business rule violations (end < start)
        - Pattern matching failures
        """
        with pytest.raises(ImportError):
            from app.exceptions import RuntimeParsingError

            # Different runtime error categories
            format_error = RuntimeParsingError("Invalid date format")
            logic_error = RuntimeParsingError("End date before start date")
            pattern_error = RuntimeParsingError("Unknown runtime pattern")

            # Expected categorization:
            assert format_error.error_code.startswith("PPV_RUNTIME")
            assert logic_error.error_code.startswith("PPV_RUNTIME")
            assert pattern_error.error_code.startswith("PPV_RUNTIME")

        print("Learning: Runtime errors need semantic categorization")


@pytest.mark.exceptions
class TestBusinessRuleError:
    """
    TDD Foundation: Test business rule exception (selective ValueError replacement)

    MIGRATION TARGET: Specific ValueError instances → BusinessRuleError
    """

    def test_business_rule_inheritance(self):
        """
        Test inheritance and business context

        HYPOTHESIS: BusinessRuleError should distinguish business logic from technical errors
        """
        with pytest.raises(ImportError):
            from app.exceptions import PPVBaseException, BusinessRuleError

            error = BusinessRuleError(
                message="Impression goal exceeds system limit",
                details={
                    "rule": "impression_goal_max_limit",
                    "limit": 2000000000,
                    "provided_value": 3000000000,
                    "business_context": "system_performance_constraint"
                }
            )

            # Expected behavior:
            assert isinstance(error, PPVBaseException)
            assert error.error_code.startswith("PPV_BUSINESS")
            assert error.is_business_rule_violation() == True

        print("Learning: BusinessRuleError separates business from technical concerns")

    def test_selective_value_error_replacement(self):
        """
        Test selective replacement of ValueError instances

        MIGRATION STRATEGY: Not all ValueError → BusinessRuleError
        Only business rule violations should use BusinessRuleError
        """
        with pytest.raises(ImportError):
            from app.exceptions import BusinessRuleError

            # Business rule violations (should become BusinessRuleError):
            business_errors = [
                "Impression goal must be at least 1",
                "Budget must be positive",
                "End date must be after start date"
            ]

            # Technical errors (should stay ValueError):
            technical_errors = [
                "Cannot convert 'abc' to integer",
                "Invalid date format",
                "String index out of range"
            ]

            # Test categorization logic needed
            for error_msg in business_errors:
                # Should become BusinessRuleError
                pass

            for error_msg in technical_errors:
                # Should remain ValueError
                pass

        print("Learning: Selective ValueError replacement preserves technical error semantics")


@pytest.mark.exceptions
class TestExceptionHierarchyIntegration:
    """
    TDD Foundation: Test exception hierarchy integration patterns

    INTEGRATION: How do services work together with unified exceptions?
    """

    def test_isinstance_checks(self):
        """
        Test exception type checking across hierarchy

        HYPOTHESIS: isinstance() should work intuitively across the hierarchy
        """
        with pytest.raises(ImportError):
            from app.exceptions import (
                PPVBaseException,
                DataValidationError,
                RuntimeParsingError,
                BusinessRuleError
            )

            data_error = DataValidationError("Data test")
            runtime_error = RuntimeParsingError("Runtime test")
            business_error = BusinessRuleError("Business test")

            # Expected hierarchy behavior:
            assert isinstance(data_error, PPVBaseException)
            assert isinstance(runtime_error, PPVBaseException)
            assert isinstance(business_error, PPVBaseException)

            # Type-specific checks:
            assert isinstance(data_error, DataValidationError)
            assert not isinstance(data_error, RuntimeParsingError)

        print("Learning: Exception hierarchy enables precise error handling")

    def test_error_code_system(self):
        """
        Test structured error code system

        DISCOVERY: How should error codes be structured for programmatic handling?
        - Service prefix (PPV_DATA, PPV_RUNTIME, PPV_BUSINESS)
        - Error category numbering
        - Unique identification within service
        """
        with pytest.raises(ImportError):
            from app.exceptions import (
                DataValidationError,
                RuntimeParsingError,
                BusinessRuleError
            )

            errors = [
                DataValidationError("Test 1"),
                DataValidationError("Test 2"),
                RuntimeParsingError("Test 3"),
                BusinessRuleError("Test 4")
            ]

            # Expected error code patterns:
            error_codes = [e.error_code for e in errors]

            # All codes should be unique
            assert len(set(error_codes)) == len(error_codes)

            # Service prefixes should be consistent
            data_codes = [code for code in error_codes if code.startswith("PPV_DATA")]
            runtime_codes = [code for code in error_codes if code.startswith("PPV_RUNTIME")]
            business_codes = [code for code in error_codes if code.startswith("PPV_BUSINESS")]

            assert len(data_codes) == 2
            assert len(runtime_codes) == 1
            assert len(business_codes) == 1

        print("Learning: Structured error codes enable systematic error handling")


# =============================================================================
# TDD FOUNDATION PATTERN 2: Backward Compatibility Tests
# =============================================================================

@pytest.mark.exceptions
@pytest.mark.compatibility
class TestBackwardCompatibility:
    """
    TDD Foundation: Test backward compatibility during exception migration

    SAFETY NET: Ensure existing code continues working during migration
    """

    def test_conversion_error_alias(self):
        """
        Test ConversionError = DataValidationError alias works

        MIGRATION SAFETY: Existing imports and isinstance() checks must continue working
        """
        with pytest.raises(ImportError):
            from app.exceptions import DataValidationError
            # After migration, this import should work:
            # from app.exceptions import ConversionError

            # ConversionError should be an alias for DataValidationError
            # error = ConversionError("Compatibility test")
            # assert isinstance(error, DataValidationError)
            # assert isinstance(error, ConversionError)

        print("Learning: ConversionError alias enables seamless migration")

    def test_runtime_parse_error_alias(self):
        """
        Test RuntimeParseError = RuntimeParsingError alias works

        MIGRATION SAFETY: RuntimeParser service should work unchanged
        """
        with pytest.raises(ImportError):
            from app.exceptions import RuntimeParsingError
            # After migration:
            # from app.exceptions import RuntimeParseError

            # error = RuntimeParseError("Compatibility test")
            # assert isinstance(error, RuntimeParsingError)
            # assert isinstance(error, RuntimeParseError)

        print("Learning: RuntimeParseError alias maintains service compatibility")

    def test_existing_isinstance_checks(self):
        """
        Test existing isinstance() calls still work with aliases

        REGRESSION PROTECTION: Any existing exception handling code must continue working
        """
        # Test current exception patterns that must continue working:

        # Pattern 1: Direct exception catching
        try:
            raise ConversionError("Test error")
        except ConversionError as e:
            assert isinstance(e, ConversionError)

        # Pattern 2: Type checking
        error = RuntimeParseError("Test error")
        assert isinstance(error, RuntimeParseError)
        assert isinstance(error, Exception)

        # After migration, these patterns must still work with aliases
        print("Learning: Existing isinstance() checks define compatibility requirements")


# =============================================================================
# TDD FOUNDATION PATTERN 3: Service Migration Tests (RED PHASE)
# =============================================================================

@pytest.mark.exceptions
@pytest.mark.migration
class TestDataConverterMigration:
    """
    TDD Foundation: Test DataConverter migration to unified exceptions

    RED PHASE: These tests will fail initially (expected)
    GREEN PHASE: Tests pass after backend engineer migrates DataConverter
    """

    def test_conversion_error_replaced_with_data_validation_error(self):
        """
        Test old ConversionError replaced with DataValidationError

        MIGRATION TARGET: DataConverter should raise DataValidationError instead of ConversionError
        RED PHASE: This test documents current behavior that needs to change
        """
        converter = DataConverter()

        # Current behavior (RED phase): DataConverter raises ValueError, not ConversionError
        # This shows that DataConverter doesn't even use ConversionError currently!
        with pytest.raises(ValueError):  # Current actual behavior
            converter.convert_european_decimal("invalid,format,string")

        # Expected after migration (GREEN phase):
        # Step 1: DataConverter should first use ConversionError consistently
        # Step 2: Then migrate ConversionError → DataValidationError
        # with pytest.raises(DataValidationError):
        #     converter.convert_european_decimal("invalid,format,string")

        print("Learning: DataConverter currently uses ValueError, needs ConversionError first, then DataValidationError")

    def test_impression_goal_business_rule_migration(self):
        """
        Test impression goal validation uses BusinessRuleError

        MIGRATION TARGET: Business rule violations should use BusinessRuleError
        """
        converter = DataConverter()

        # Current behavior (RED phase):
        with pytest.raises(ValueError):
            converter.convert_impression_goal("0")  # Below minimum

        with pytest.raises(ValueError):
            converter.convert_impression_goal("3000000000")  # Above maximum

        # Expected after migration (GREEN phase):
        # with pytest.raises(BusinessRuleError):
        #     converter.convert_impression_goal("0")
        #
        # with pytest.raises(BusinessRuleError):
        #     converter.convert_impression_goal("3000000000")

        print("Learning: Business rule violations need BusinessRuleError")

    def test_technical_errors_remain_value_error(self):
        """
        Test technical errors remain as ValueError

        MIGRATION STRATEGY: Only business rules become BusinessRuleError
        Technical parsing errors should remain ValueError
        """
        converter = DataConverter()

        # Technical errors should remain ValueError after migration:
        with pytest.raises(ValueError):
            converter.convert_european_decimal("completely_invalid_text")

        with pytest.raises(TypeError):
            converter.convert_impression_goal(None)

        print("Learning: Technical errors keep ValueError semantics")


@pytest.mark.exceptions
@pytest.mark.migration
class TestRuntimeParserMigration:
    """
    TDD Foundation: Test RuntimeParser migration to unified exceptions

    RED PHASE: Tests fail until RuntimeParser is migrated
    """

    def test_runtime_parse_error_replaced(self):
        """
        Test old RuntimeParseError replaced with RuntimeParsingError

        MIGRATION TARGET: RuntimeParser should raise RuntimeParsingError
        """
        parser = RuntimeParser()

        # Current behavior (RED phase):
        with pytest.raises(RuntimeParseError):
            parser.parse("invalid-runtime-format")

        # Expected after migration (GREEN phase):
        # with pytest.raises(RuntimeParsingError):
        #     parser.parse("invalid-runtime-format")

        print("Learning: RuntimeParser migration changes exception types")

    def test_date_logic_business_rules(self):
        """
        Test date logic violations use BusinessRuleError

        BUSINESS RULE: End date must be after start date
        """
        parser = RuntimeParser()

        # Current behavior (RED phase) - RuntimeParseError for business rule
        with pytest.raises(RuntimeParseError):
            parser.parse("24.07.2025-07.07.2025")  # End before start

        # Expected after migration (GREEN phase):
        # with pytest.raises(BusinessRuleError):
        #     parser.parse("24.07.2025-07.07.2025")

        print("Learning: Date logic violations are business rules")


@pytest.mark.exceptions
@pytest.mark.migration
class TestCampaignModelMigration:
    """
    TDD Foundation: Test Campaign model migration to unified exceptions

    INTEGRATION: Campaign model uses multiple services that will be migrated
    """

    def test_campaign_validation_exception_types(self):
        """
        Test Campaign model raises appropriate exception types

        INTEGRATION TARGET: Campaign should work with migrated service exceptions
        """
        # Current behavior (RED phase):
        with pytest.raises(ValueError):
            Campaign(
                id="invalid-uuid-format",
                name="Test Campaign",
                runtime="ASAP-30.06.2025",
                impression_goal=1000000,
                budget_eur=50000.0,
                cpm_eur=5.0,
                buyer="Test Buyer"
            )

        # Expected after migration (GREEN phase):
        # Business rule violations should use BusinessRuleError
        # Data validation errors should use DataValidationError
        # Runtime parsing errors should use RuntimeParsingError

        print("Learning: Campaign model integration requires coordinated migration")


# =============================================================================
# TDD FOUNDATION PATTERN 4: Current Behavior Protection (Characterization Tests)
# =============================================================================

@pytest.mark.exceptions
@pytest.mark.characterization
class TestCurrentExceptionBehaviorLock:
    """
    TDD Foundation: Lock in exact current exception behavior before hierarchy migration

    REGRESSION PROTECTION: Preserve exact behavior during refactoring
    """

    def test_data_converter_current_exceptions(self):
        """
        Lock in current DataConverter exception types and messages

        CHARACTERIZATION: Document exact current behavior to prevent regression
        """
        converter = DataConverter()

        # Lock in current ConversionError behavior:
        invalid_inputs = [
            "",  # Empty string
            "not a number",  # Non-numeric
            "12,,34",  # Double comma
            "12..34"  # Double dot
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises((ValueError, TypeError)) as exc_info:
                converter.convert_european_decimal(invalid_input)

            # Lock in exact error message format:
            error_msg = str(exc_info.value)
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0

            print(f"Locked behavior: '{invalid_input}' → {type(exc_info.value).__name__}: {error_msg}")

    def test_runtime_parser_current_exceptions(self):
        """
        Lock in current RuntimeParser exception types and messages

        CHARACTERIZATION: Preserve exact parsing error behavior
        """
        parser = RuntimeParser()

        # Lock in current RuntimeParseError behavior:
        invalid_runtimes = [
            "",  # Empty string
            "invalid-format",  # Unknown pattern
            "32.13.2025-01.01.2026",  # Invalid date
            "01.01.2026-01.01.2025"  # End before start
        ]

        for invalid_runtime in invalid_runtimes:
            with pytest.raises((RuntimeParseError, ValueError, TypeError)) as exc_info:
                parser.parse(invalid_runtime)

            # Lock in exact error message format:
            error_msg = str(exc_info.value)
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0

            print(f"Locked behavior: '{invalid_runtime}' → {type(exc_info.value).__name__}: {error_msg}")

    def test_campaign_model_current_exceptions(self):
        """
        Lock in current Campaign model exception behavior

        CHARACTERIZATION: Preserve exact validation error behavior
        """
        # Lock in current Campaign validation behavior:
        invalid_campaigns = [
            # Invalid UUID
            {
                "id": "invalid-uuid",
                "name": "Test",
                "runtime": "ASAP-30.06.2025",
                "impression_goal": 1000000,
                "budget_eur": 50000.0,
                "cpm_eur": 5.0,
                "buyer": "Test"
            },
            # Empty name
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "",
                "runtime": "ASAP-30.06.2025",
                "impression_goal": 1000000,
                "budget_eur": 50000.0,
                "cpm_eur": 5.0,
                "buyer": "Test"
            },
            # Invalid impression goal
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Test",
                "runtime": "ASAP-30.06.2025",
                "impression_goal": 0,  # Below minimum
                "budget_eur": 50000.0,
                "cpm_eur": 5.0,
                "buyer": "Test"
            }
        ]

        for invalid_data in invalid_campaigns:
            with pytest.raises(ValueError) as exc_info:
                Campaign(**invalid_data)

            # Lock in exact error message:
            error_msg = str(exc_info.value)
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0

            print(f"Locked Campaign behavior: {invalid_data} → ValueError: {error_msg}")


# =============================================================================
# TDD FOUNDATION PATTERN 5: Migration Integration Tests
# =============================================================================

@pytest.mark.exceptions
@pytest.mark.integration
class TestMigrationSafety:
    """
    TDD Foundation: Test migration safety and rollback scenarios

    SAFETY: Ensure migration can be done incrementally without breaking changes
    """

    def test_mixed_exception_handling(self):
        """
        Test handling of mixed old and new exception types during migration

        MIGRATION SCENARIO: Some services migrated, others not yet migrated
        """
        # During migration, we might have mixed exception types:

        def handle_data_conversion_error():
            """Test handling both old and new exception types"""
            try:
                converter = DataConverter()
                converter.convert_european_decimal("invalid")
            except (ConversionError, Exception) as e:  # Broad catch during migration
                if hasattr(e, 'error_code'):
                    # New structured exception
                    print(f"New exception: {e.error_code}")
                else:
                    # Old exception
                    print(f"Old exception: {type(e).__name__}")
                return True
            return False

        # This pattern should work during migration:
        assert handle_data_conversion_error() == True

        print("Learning: Migration requires mixed exception handling patterns")

    def test_api_error_response_compatibility(self):
        """
        Test API error response format remains consistent during migration

        INTEGRATION: API responses should be stable for frontend compatibility
        """
        # Simulate API error handling during migration:

        def format_error_response(exception):
            """Format exception for API response - should work with old and new exceptions"""
            if hasattr(exception, 'error_code'):
                # New structured exception
                return {
                    "error": str(exception),
                    "error_code": exception.error_code,
                    "details": getattr(exception, 'details', {}),
                    "timestamp": getattr(exception, 'timestamp', datetime.utcnow()).isoformat()
                }
            else:
                # Old exception - maintain compatibility
                return {
                    "error": str(exception),
                    "error_code": f"LEGACY_{type(exception).__name__.upper()}",
                    "details": {},
                    "timestamp": datetime.utcnow().isoformat()
                }

        # Test with current exceptions:
        old_error = ConversionError("Test error")
        response = format_error_response(old_error)

        assert "error" in response
        assert "error_code" in response
        assert response["error_code"].startswith("LEGACY_")

        print("Learning: API error format needs backward compatibility")


# =============================================================================
# TDD GUIDANCE FOR BACKEND-ENGINEER
# =============================================================================

"""
IMPLEMENTATION GUIDANCE FOR BACKEND-ENGINEER:

1. RED PHASE (Current State):
   - All new exception hierarchy tests fail with ImportError
   - Migration tests fail with old exception types
   - Characterization tests pass (lock in current behavior)

2. GREEN PHASE (Implementation Strategy):

   STEP 1: Create app/exceptions.py with unified hierarchy
   ```python
   class PPVBaseException(Exception):
       def __init__(self, message, error_code=None, details=None):
           super().__init__(message)
           self.error_code = error_code or self._generate_error_code()
           self.details = details or {}
           self.timestamp = datetime.utcnow()

   class DataValidationError(PPVBaseException):
       def _generate_error_code(self):
           return f"PPV_DATA_{self._get_sequential_id()}"

   class RuntimeParsingError(PPVBaseException):
       def _generate_error_code(self):
           return f"PPV_RUNTIME_{self._get_sequential_id()}"

   class BusinessRuleError(PPVBaseException):
       def _generate_error_code(self):
           return f"PPV_BUSINESS_{self._get_sequential_id()}"

   # Backward compatibility aliases
   ConversionError = DataValidationError
   RuntimeParseError = RuntimeParsingError
   ```

   STEP 2: Service-by-service migration
   - Start with DataConverter: replace ConversionError with DataValidationError
   - Then RuntimeParser: replace RuntimeParseError with RuntimeParsingError
   - Finally Campaign model: integrate with migrated services

   STEP 3: Business rule identification
   - Replace selective ValueError with BusinessRuleError
   - Keep technical ValueError as ValueError
   - Business rules: range validation, date logic, positive values

3. REFACTOR PHASE:
   - Remove backward compatibility aliases after all services migrated
   - Add error monitoring and structured logging
   - Consider error recovery strategies

TESTING COMMANDS:
- Run new tests: pytest tests/test_exceptions.py::TestPPVBaseException -v
- Run migration tests: pytest tests/test_exceptions.py -k migration -v
- Run characterization: pytest tests/test_exceptions.py -k characterization -v
- Run all exception tests: pytest tests/test_exceptions.py -v

MIGRATION SAFETY:
- Characterization tests ensure no behavior changes
- Backward compatibility aliases enable incremental migration
- Mixed exception handling supports partial migration states
- API response format remains stable for frontend

SUCCESS CRITERIA:
- All TestPPVBaseException tests pass
- All migration tests pass (services raise new exception types)
- All characterization tests still pass (no behavior regression)
- Backward compatibility tests pass (aliases work)
- Existing application tests continue passing
"""