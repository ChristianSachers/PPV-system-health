"""
Campaign Data Validator - Reusable Validation Components

This module provides reusable validation functions that can be used
across different models and services. It focuses on generic validations
that provide real value when extracted from model constructors.

Educational Focus: How to design validators that are truly reusable
rather than just moving complexity from one place to another.
"""

from uuid import UUID
from typing import Union


class CampaignDataValidator:
    """
    Reusable data validation utilities.

    This class contains only validations that are genuinely reusable
    across multiple models or contexts. Campaign-specific business rules
    remain in the Campaign model where they belong.
    """

    @staticmethod
    def validate_uuid(uuid_string: Union[str, None]) -> str:
        """
        Validate UUID format and return normalized string.

        Args:
            uuid_string: String to validate as UUID

        Returns:
            str: Validated UUID string

        Raises:
            ValueError: If UUID format is invalid

        Example:
            >>> validator = CampaignDataValidator()
            >>> result = validator.validate_uuid("56cc787c-a703-4cd3-995a-4b42eb408dfb")
            >>> assert result == "56cc787c-a703-4cd3-995a-4b42eb408dfb"
        """
        if uuid_string is None:
            raise ValueError("UUID cannot be None")

        if not isinstance(uuid_string, str):
            raise ValueError("UUID must be a string")

        if not uuid_string.strip():
            raise ValueError("UUID cannot be empty")

        try:
            # Validate by parsing as UUID and converting back to string
            uuid_obj = UUID(uuid_string)
            return str(uuid_obj)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format: {uuid_string}") from e

    @staticmethod
    def validate_positive_number(value: Union[int, float, None], field_name: str) -> Union[int, float]:
        """
        Validate that a numeric value is positive.

        Args:
            value: Numeric value to validate
            field_name: Name of the field being validated (for error messages)

        Returns:
            Union[int, float]: Validated positive value

        Raises:
            ValueError: If value is not positive or not numeric

        Example:
            >>> validator = CampaignDataValidator()
            >>> result = validator.validate_positive_number(100.5, "Budget")
            >>> assert result == 100.5
        """
        if value is None:
            raise ValueError(f"{field_name} cannot be None")

        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be a number, got: {type(value).__name__}")

        if value <= 0:
            raise ValueError(f"{field_name} must be positive, got: {value}")

        return value

    @staticmethod
    def validate_non_empty_string(text: Union[str, None], field_name: str) -> str:
        """
        Validate that a string is not empty or whitespace-only.

        Args:
            text: String to validate
            field_name: Name of the field being validated (for error messages)

        Returns:
            str: Validated non-empty string

        Raises:
            ValueError: If string is empty, whitespace-only, or not a string

        Example:
            >>> validator = CampaignDataValidator()
            >>> result = validator.validate_non_empty_string("Test Campaign", "Campaign Name")
            >>> assert result == "Test Campaign"
        """
        if text is None:
            raise ValueError(f"{field_name} cannot be None")

        if not isinstance(text, str):
            raise ValueError(f"{field_name} must be a string, got: {type(text).__name__}")

        if not text.strip():
            raise ValueError(f"{field_name} cannot be empty")

        return text

    @staticmethod
    def validate_required_field(value, field_name: str):
        """
        Validate that a required field is not None.

        Args:
            value: Value to check
            field_name: Name of the field being validated

        Returns:
            The original value if valid

        Raises:
            ValueError: If value is None

        Example:
            >>> validator = CampaignDataValidator()
            >>> result = validator.validate_required_field("buyer_name", "Buyer")
            >>> assert result == "buyer_name"
        """
        if value is None:
            raise ValueError(f"{field_name} field is required")

        return value


# =============================================================================
# VALIDATION UTILITIES FOR SPECIFIC DATA TYPES
# =============================================================================

class ValidationUtils:
    """
    Additional validation utilities that might be useful across the application.

    These are optional extensions to the core CampaignDataValidator.
    """

    @staticmethod
    def validate_email_format(email: str, field_name: str = "Email") -> str:
        """
        Validate basic email format.

        Note: This is a simple validation. For production, consider using
        a proper email validation library.
        """
        if not email or "@" not in email:
            raise ValueError(f"{field_name} must be a valid email format")
        return email

    @staticmethod
    def validate_percentage_range(value: float, field_name: str = "Percentage") -> float:
        """
        Validate that a value is within percentage range (0-100).
        """
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be a number")

        if not 0 <= value <= 100:
            raise ValueError(f"{field_name} must be between 0 and 100, got: {value}")

        return value

    @staticmethod
    def validate_date_range(start_date, end_date, field_prefix: str = "Date") -> tuple:
        """
        Validate that start_date <= end_date when both are provided.
        """
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise ValueError(f"{field_prefix} start cannot be after {field_prefix.lower()} end")

        return start_date, end_date


# =============================================================================
# USAGE EXAMPLES AND DOCUMENTATION
# =============================================================================

"""
USAGE EXAMPLES:
==============

# In Campaign model constructor:
from app.validators.campaign_data_validator import CampaignDataValidator

def __init__(self, **kwargs):
    validator = CampaignDataValidator()

    # Extract reusable validations
    if 'id' in kwargs:
        kwargs['id'] = validator.validate_uuid(kwargs['id'])

    if 'budget_eur' in kwargs:
        kwargs['budget_eur'] = validator.validate_positive_number(kwargs['budget_eur'], 'Budget')

    if 'name' in kwargs:
        kwargs['name'] = validator.validate_non_empty_string(kwargs['name'], 'Campaign Name')

    # Keep campaign-specific validations in the constructor
    if 'impression_goal' in kwargs:
        kwargs['impression_goal'] = self.validate_impression_goal_range(kwargs['impression_goal'])

    # Continue with other constructor logic...

DESIGN PRINCIPLES:
=================

1. EXTRACT ONLY TRULY REUSABLE VALIDATIONS:
   ✅ UUID validation - used by any model with UUID primary key
   ✅ Positive number validation - used by financial fields across models
   ✅ Non-empty string validation - used by required text fields

2. KEEP DOMAIN-SPECIFIC LOGIC IN MODELS:
   ❌ Don't extract impression_goal_range - campaign-specific business rule
   ❌ Don't extract buyer_validation - campaign-specific logic
   ❌ Don't extract date_logic - depends on domain context

3. MAINTAIN CLEAR ERROR MESSAGES:
   - Error messages should be as specific as possible
   - Include field names in error messages for better debugging
   - Preserve existing error message formats for backward compatibility

4. AVOID OVER-ABSTRACTION:
   - Don't create validators for one-off validations
   - Don't extract logic that's only used in one place
   - Don't create complex validator hierarchies unless truly needed

TESTING STRATEGY:
================

This validator is designed to work with the TDD tests in:
/tests/test_validators/test_campaign_data_validator.py

The tests ensure that:
✅ Valid inputs produce expected outputs
✅ Invalid inputs produce appropriate error messages
✅ Error messages are consistent and helpful
✅ Type checking works correctly
✅ Edge cases are handled properly
"""