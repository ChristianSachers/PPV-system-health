"""
Campaign Data Validator TDD Tests - RED PHASE

This file contains tests for the extracted CampaignDataValidator class.
These tests will fail initially (RED phase) and guide the implementation
of truly reusable validation components.

Educational Focus: How to design validators that provide real value
rather than just moving constructor complexity around.
"""

import pytest
from datetime import date
from uuid import uuid4


# =============================================================================
# RED PHASE - Tests for CampaignDataValidator (not yet implemented)
# =============================================================================

class TestCampaignDataValidator:
    """
    TDD RED PHASE: Test design for reusable validation components

    These tests define what the CampaignDataValidator should do:
    1. Validate UUIDs (reusable across any model)
    2. Validate positive numbers (reusable financial validation)
    3. Validate non-empty strings (reusable text validation)

    Key Insight: Only extract validations that are TRULY reusable
    """

    def test_uuid_validation_success(self):
        """Test UUID validation with valid UUID strings"""
        # GREEN PHASE: CampaignDataValidator is now implemented
        from app.validators.campaign_data_validator import CampaignDataValidator

        valid_uuids = [
            "56cc787c-a703-4cd3-995a-4b42eb408dfb",
            "12345678-1234-1234-1234-123456789012",
            str(uuid4())
        ]

        validator = CampaignDataValidator()

        for uuid_string in valid_uuids:
            result = validator.validate_uuid(uuid_string)
            assert result == uuid_string
            assert isinstance(result, str)

        print("GREEN PHASE: UUID validation success test passing")

    def test_uuid_validation_failure(self):
        """Test UUID validation with invalid UUID strings"""
        # GREEN PHASE: CampaignDataValidator is now implemented
        from app.validators.campaign_data_validator import CampaignDataValidator

        invalid_uuids = [
            ("not-a-uuid", "Invalid UUID format"),
            ("12345678-1234-1234-1234", "Invalid UUID format"),  # Too short
            ("", "UUID cannot be empty"),
            (None, "UUID cannot be None"),
            (123456789, "UUID must be a string")
        ]

        validator = CampaignDataValidator()

        for invalid_uuid, expected_error in invalid_uuids:
            with pytest.raises(ValueError, match=expected_error):
                validator.validate_uuid(invalid_uuid)

        print("GREEN PHASE: UUID validation failure test passing")

    def test_positive_number_validation_success(self):
        """Test positive number validation with valid values"""
        # GREEN PHASE: CampaignDataValidator is now implemented
        from app.validators.campaign_data_validator import CampaignDataValidator

        valid_values = [
            (1.0, "Budget"),
            (100.5, "CPM"),
            (1500000, "Impression Goal"),
            (0.01, "Minimum Value")
        ]

        validator = CampaignDataValidator()

        for value, field_name in valid_values:
            result = validator.validate_positive_number(value, field_name)
            assert result == value
            assert result > 0

        print("GREEN PHASE: Positive number validation success test passing")

    def test_positive_number_validation_failure(self):
        """Test positive number validation with invalid values"""
        # GREEN PHASE: CampaignDataValidator is now implemented
        from app.validators.campaign_data_validator import CampaignDataValidator

        invalid_values = [
            (0, "Zero Value", "Zero Value must be positive"),
            (-1.0, "Negative Budget", "Negative Budget must be positive"),
            (-100, "Negative Impression Goal", "Negative Impression Goal must be positive"),
            (None, "None Value", "None Value cannot be None"),
            ("string", "String Value", "String Value must be a number")
        ]

        validator = CampaignDataValidator()

        for value, field_name, expected_error in invalid_values:
            with pytest.raises(ValueError, match=expected_error):
                validator.validate_positive_number(value, field_name)

        print("GREEN PHASE: Positive number validation failure test passing")

    def test_non_empty_string_validation_success(self):
        """Test non-empty string validation with valid strings"""
        # GREEN PHASE: CampaignDataValidator is now implemented
        from app.validators.campaign_data_validator import CampaignDataValidator

        valid_strings = [
            ("Test Campaign", "Campaign Name"),
            ("Not set", "Buyer"),
            ("ASAP-30.06.2025", "Runtime"),
            ("A", "Single Character")
        ]

        validator = CampaignDataValidator()

        for string_value, field_name in valid_strings:
            result = validator.validate_non_empty_string(string_value, field_name)
            assert result == string_value
            assert len(result.strip()) > 0

        print("GREEN PHASE: Non-empty string validation success test passing")

    def test_non_empty_string_validation_failure(self):
        """Test non-empty string validation with invalid strings"""
        # GREEN PHASE: CampaignDataValidator is now implemented
        from app.validators.campaign_data_validator import CampaignDataValidator

        invalid_strings = [
            ("", "Empty String", "Empty String cannot be empty"),
            ("   ", "Whitespace Only", "Whitespace Only cannot be empty"),
            (None, "None Value", "None Value cannot be None"),
            (123, "Not a String", "Not a String must be a string")
        ]

        validator = CampaignDataValidator()

        for string_value, field_name, expected_error in invalid_strings:
            with pytest.raises(ValueError, match=expected_error):
                validator.validate_non_empty_string(string_value, field_name)

        print("GREEN PHASE: Non-empty string validation failure test passing")


# =============================================================================
# RED PHASE - Tests for CampaignDataCleaner (not yet implemented)
# =============================================================================

class TestCampaignDataCleaner:
    """
    TDD RED PHASE: Test design for data cleaning utility

    This class should handle field corrections and data normalization
    that are specific to campaign data quality issues.
    """

    def test_field_corrections_application(self):
        """Test field corrections for known data quality issues"""
        # GREEN PHASE: CampaignDataCleaner is now implemented
        from app.validators.campaign_data_cleaner import CampaignDataCleaner

        # Test cmp_eur -> cpm_eur correction
        dirty_data = {
            "id": str(uuid4()),
            "name": "Test Campaign",
            "cmp_eur": 2.5,  # Typo: should be cpm_eur
            "budget_eur": 10000.0,
            "buyer": "Not set"
        }

        cleaner = CampaignDataCleaner()
        cleaned_data = cleaner.apply_field_corrections(dirty_data)

        assert "cpm_eur" in cleaned_data
        assert cleaned_data["cpm_eur"] == 2.5
        assert "cmp_eur" not in cleaned_data  # Original typo removed

        print("GREEN PHASE: Field corrections test passing")

    def test_field_corrections_preserves_clean_data(self):
        """Test that field corrections don't break already clean data"""
        # GREEN PHASE: CampaignDataCleaner is now implemented
        from app.validators.campaign_data_cleaner import CampaignDataCleaner

        clean_data = {
            "id": str(uuid4()),
            "name": "Test Campaign",
            "cpm_eur": 2.5,  # Already correct
            "budget_eur": 10000.0,
            "buyer": "Not set"
        }

        cleaner = CampaignDataCleaner()
        result_data = cleaner.apply_field_corrections(clean_data)

        assert result_data == clean_data  # Should be unchanged

        print("GREEN PHASE: Clean data preservation test passing")


# =============================================================================
# REFACTORED CONSTRUCTOR BEHAVIOR TESTS
# =============================================================================

class TestRefactoredConstructorBehavior:
    """
    TDD RED PHASE: Test design for refactored constructor

    These tests ensure the refactored constructor maintains
    exact same behavior while using extracted components.
    """

    def test_refactored_constructor_identical_behavior(self, test_db_session):
        """Test that refactored constructor produces identical results"""
        # This test will fail until refactoring is implemented
        campaign_data = {
            "id": "56cc787c-a703-4cd3-995a-4b42eb408dfb",
            "name": "Refactored Constructor Test",
            "runtime": "07.07.2025-24.07.2025",
            "impression_goal": 1500000,
            "budget_eur": 15000.75,
            "cpm_eur": 2.55,
            "buyer": "Test Buyer"
        }

        # Create campaign with current constructor
        from app.models.campaign import Campaign
        current_campaign = Campaign(**campaign_data)

        # TODO: After refactoring, ensure behavior is identical
        # refactored_campaign = RefactoredCampaign(**campaign_data)
        # assert current_campaign.id == refactored_campaign.id
        # assert current_campaign.entity_type == refactored_campaign.entity_type
        # assert current_campaign.is_running == refactored_campaign.is_running

        print("RED PHASE: Refactored constructor behavior test defined")

    def test_refactored_constructor_error_messages_identical(self):
        """Test that refactored constructor produces identical error messages"""
        campaign_data = {
            "id": "invalid-uuid",  # This should trigger same error
            "name": "Error Message Test",
            "runtime": "ASAP-30.06.2025",
            "impression_goal": 1000000,
            "budget_eur": 10000.0,
            "cpm_eur": 2.0,
            "buyer": "Not set"
        }

        # Current constructor error
        from app.models.campaign import Campaign
        with pytest.raises(ValueError) as current_error:
            Campaign(**campaign_data)

        # TODO: After refactoring, ensure error messages are identical
        # with pytest.raises(ValueError) as refactored_error:
        #     RefactoredCampaign(**campaign_data)
        #
        # assert str(current_error.value) == str(refactored_error.value)

        print("RED PHASE: Identical error messages test defined")


# =============================================================================
# TDD IMPLEMENTATION GUIDANCE
# =============================================================================

"""
TDD IMPLEMENTATION ROADMAP FOR CONSTRUCTOR REFACTORING:
======================================================

CURRENT STATUS: RED PHASE - All tests above will fail
NEXT STEPS: GREEN PHASE - Implement components to make tests pass

IMPLEMENTATION ORDER:

1. CREATE CampaignDataValidator:
   Location: /backend/app/validators/campaign_data_validator.py

   class CampaignDataValidator:
       @staticmethod
       def validate_uuid(uuid_string: str) -> str:
           # Implementation here

       @staticmethod
       def validate_positive_number(value: float, field_name: str) -> float:
           # Implementation here

       @staticmethod
       def validate_non_empty_string(text: str, field_name: str) -> str:
           # Implementation here

2. CREATE CampaignDataCleaner:
   Location: /backend/app/validators/campaign_data_cleaner.py

   class CampaignDataCleaner:
       @staticmethod
       def apply_field_corrections(data: dict) -> dict:
           # Handle cmp_eur -> cpm_eur correction
           # Return cleaned data dictionary

3. REFACTOR Campaign.__init__():
   - Import and use CampaignDataValidator for reusable validations
   - Import and use CampaignDataCleaner for field corrections
   - Keep campaign-specific logic in constructor
   - Maintain exact same error messages and behavior

4. RUN CHARACTERIZATION TESTS:
   - All existing behavior tests must still pass
   - Error messages must remain identical
   - No behavior changes allowed during refactoring

GREEN PHASE SUCCESS CRITERIA:
✅ All tests in this file pass
✅ All existing Campaign model tests pass
✅ All characterization tests pass
✅ Constructor is more readable
✅ Extracted components are reusable

REFACTOR PHASE:
- Optimize validator performance
- Add comprehensive documentation
- Consider additional reusable validations
- Review and clean up code organization
"""