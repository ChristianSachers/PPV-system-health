"""
DataConverter Service - European Number Format Conversion

This service handles the complex data conversion requirements for XLSX campaign data:
1. European decimal format conversion (comma as decimal separator)
2. European thousands separator handling (dot as thousands separator)
3. Impression goal INTEGER conversion with business validation
4. Financial precision handling for budget calculations

Key Business Rules:
- Impression goals: INTEGER values (1 to 2,000,000,000)
- European format: "1.234.567,89" → 1234567.89
- Budget validation: Must be positive values
- Precision: Financial calculations preserve 2 decimal places
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Union, Optional

# Import unified exception hierarchy
from app.exceptions import DataValidationError, BusinessRuleError


class ConversionError(Exception):
    """Custom exception for data conversion errors"""
    pass


class ConversionResult:
    """Result class containing conversion details"""
    def __init__(self, value: Union[float, int], original_format: str, conversion_method: str):
        self.value = value
        self.original_format = original_format
        self.conversion_method = conversion_method


class DataConverter:
    """
    Service for converting XLSX data formats to standardized Python types.

    Handles European number formats commonly found in campaign data:
    - Budget values with comma decimal separators
    - Thousands separators using dots
    - Impression goal INTEGER conversion
    - Business rule validation
    """

    # Business constraints
    MIN_IMPRESSION_GOAL = 1
    MAX_IMPRESSION_GOAL = 2_000_000_000

    @staticmethod
    def convert_european_decimal(value_string: str) -> float:
        """
        Convert European decimal format to float.

        European Format Rules:
        - Comma (,) is decimal separator: "123,45" → 123.45
        - Dot (.) is thousands separator: "1.234.567,89" → 1234567.89
        - Handle edge cases: "1234.56" (ambiguous) → treat as US format

        Args:
            value_string: String in European or US decimal format

        Returns:
            float: Converted decimal value

        Raises:
            ValueError: If string cannot be converted to valid decimal
            TypeError: If input is not a string

        Examples:
            >>> DataConverter.convert_european_decimal("2396690,38")
            2396690.38
            >>> DataConverter.convert_european_decimal("1.234.567,89")
            1234567.89
            >>> DataConverter.convert_european_decimal("1234.56")  # Ambiguous case
            1234.56
        """
        if not isinstance(value_string, str):
            raise TypeError("Input must be a string")

        if not value_string.strip():
            raise DataValidationError(
                "Input cannot be empty string",
                details={
                    "service": "DataConverter",
                    "method": "convert_european_decimal",
                    "input_value": value_string,
                    "validation_context": "empty_string_check"
                }
            )

        # Clean whitespace
        cleaned = value_string.strip()

        # Pattern matching for format detection
        # European format: optionally has dots for thousands, comma for decimal
        # US format: optionally has commas for thousands, dot for decimal

        # Check for European format indicators
        if ',' in cleaned and cleaned.count('.') > 1:
            # Definitely European: "1.234.567,89" - multiple dots + comma
            return DataConverter._convert_european_format(cleaned)
        elif ',' in cleaned and '.' not in cleaned:
            # Definitely European: "1234,56" - only comma
            return DataConverter._convert_european_format(cleaned)
        elif ',' not in cleaned and '.' in cleaned:
            # Could be US format or European thousands only: "1234.56" or "1.234"
            # Business decision: treat as US format when ambiguous
            try:
                return float(cleaned)
            except ValueError:
                raise DataValidationError(
                    f"Cannot convert '{value_string}' to decimal",
                    details={
                        "service": "DataConverter",
                        "method": "convert_european_decimal",
                        "input_value": value_string,
                        "validation_context": "US_format_conversion"
                    }
                )
        elif ',' not in cleaned and '.' not in cleaned:
            # Integer format: "1234"
            try:
                return float(cleaned)
            except ValueError:
                raise DataValidationError(
                    f"Cannot convert '{value_string}' to decimal",
                    details={
                        "service": "DataConverter",
                        "method": "convert_european_decimal",
                        "input_value": value_string,
                        "validation_context": "integer_format_conversion"
                    }
                )
        else:
            # Mixed format - try European conversion
            return DataConverter._convert_european_format(cleaned)

    @staticmethod
    def _convert_european_format(value_string: str) -> float:
        """
        Internal method to convert confirmed European format.

        Process:
        1. Remove thousands separators (dots)
        2. Replace decimal comma with dot
        3. Convert to float
        """
        # Remove thousands separators (dots), but keep decimal comma
        if ',' in value_string:
            # Split on comma to separate integer and decimal parts
            parts = value_string.split(',')
            if len(parts) != 2:
                raise DataValidationError(
                    f"Invalid European decimal format: '{value_string}' - multiple commas",
                    details={
                        "service": "DataConverter",
                        "method": "_convert_european_format",
                        "input_value": value_string,
                        "validation_context": "European_decimal_format"
                    }
                )

            integer_part = parts[0].replace('.', '')  # Remove thousands separators
            decimal_part = parts[1]

            # Validate decimal part is numeric
            if not decimal_part.isdigit():
                raise DataValidationError(
                    f"Invalid decimal part: '{decimal_part}'",
                    details={
                        "service": "DataConverter",
                        "method": "_convert_european_format",
                        "input_value": value_string,
                        "decimal_part": decimal_part,
                        "validation_context": "decimal_part_validation"
                    }
                )

            # Reconstruct as US format
            cleaned = f"{integer_part}.{decimal_part}"
        else:
            # No decimal comma, just remove thousands separators
            cleaned = value_string.replace('.', '')

        try:
            return float(cleaned)
        except ValueError:
            raise DataValidationError(
                f"Cannot convert '{value_string}' to decimal",
                details={
                    "service": "DataConverter",
                    "method": "_convert_european_format",
                    "input_value": value_string,
                    "cleaned_value": cleaned,
                    "validation_context": "European_format_conversion"
                }
            )

    @staticmethod
    def convert_impression_goal(value_string: str) -> int:
        """
        Convert impression goal string to INTEGER value.

        Business Rules:
        - Must be INTEGER (no decimal values)
        - Range: 1 to 2,000,000,000 (system limit)
        - No European formatting for impression goals (pure integers)

        Args:
            value_string: String representation of impression goal

        Returns:
            int: Converted impression goal value

        Raises:
            ValueError: If value is outside valid range or invalid format
            TypeError: If input is not a string

        Examples:
            >>> DataConverter.convert_impression_goal("2000000000")
            2000000000
            >>> DataConverter.convert_impression_goal("1500000")
            1500000
        """
        if not isinstance(value_string, str):
            raise TypeError("Input must be a string")

        if not value_string.strip():
            raise DataValidationError(
                "Impression goal cannot be empty",
                details={
                    "service": "DataConverter",
                    "method": "convert_impression_goal",
                    "input_value": value_string,
                    "validation_context": "empty_impression_goal"
                }
            )

        cleaned = value_string.strip()

        # Impression goals should be pure integers (no decimal formatting)
        if not cleaned.isdigit():
            raise DataValidationError(
                f"Impression goal must be integer value: '{value_string}'",
                details={
                    "service": "DataConverter",
                    "method": "convert_impression_goal",
                    "input_value": value_string,
                    "validation_context": "integer_format_validation"
                }
            )

        try:
            value = int(cleaned)
        except ValueError:
            raise DataValidationError(
                f"Cannot convert '{value_string}' to integer",
                details={
                    "service": "DataConverter",
                    "method": "convert_impression_goal",
                    "input_value": value_string,
                    "validation_context": "integer_conversion"
                }
            )

        # Business validation: check range
        if value < DataConverter.MIN_IMPRESSION_GOAL:
            raise BusinessRuleError(
                f"Impression goal must be at least {DataConverter.MIN_IMPRESSION_GOAL}: {value}",
                details={
                    "service": "DataConverter",
                    "method": "convert_impression_goal",
                    "business_rule": "impression_goal_minimum",
                    "provided_value": value,
                    "limit": DataConverter.MIN_IMPRESSION_GOAL,
                    "business_context": "system_performance_constraint"
                }
            )

        if value > DataConverter.MAX_IMPRESSION_GOAL:
            raise BusinessRuleError(
                f"Impression goal cannot exceed {DataConverter.MAX_IMPRESSION_GOAL}: {value}",
                details={
                    "service": "DataConverter",
                    "method": "convert_impression_goal",
                    "business_rule": "impression_goal_maximum",
                    "provided_value": value,
                    "limit": DataConverter.MAX_IMPRESSION_GOAL,
                    "business_context": "system_performance_constraint"
                }
            )

        return value

    @staticmethod
    def validate_numeric_range(value: float, min_val: float, max_val: float) -> bool:
        """
        Validate that a numeric value is within specified range.

        Args:
            value: Numeric value to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)

        Returns:
            bool: True if value is within range

        Raises:
            ValueError: If value is outside range

        Examples:
            >>> DataConverter.validate_numeric_range(1000.0, 0.0, 2000.0)
            True
            >>> DataConverter.validate_numeric_range(-100.0, 0.0, 2000.0)
            ValueError: Value -100.0 is below minimum 0.0
        """
        if value < min_val:
            raise BusinessRuleError(
                f"Value {value} is below minimum {min_val}",
                details={
                    "service": "DataConverter",
                    "method": "validate_numeric_range",
                    "business_rule": "numeric_range_minimum",
                    "provided_value": value,
                    "limit": min_val,
                    "business_context": "range_validation"
                }
            )

        if value > max_val:
            raise BusinessRuleError(
                f"Value {value} exceeds maximum {max_val}",
                details={
                    "service": "DataConverter",
                    "method": "validate_numeric_range",
                    "business_rule": "numeric_range_maximum",
                    "provided_value": value,
                    "limit": max_val,
                    "business_context": "range_validation"
                }
            )

        return True

    @staticmethod
    def convert_batch_european_decimal(value_strings: list[str]) -> list[float]:
        """
        Convert multiple European decimal values efficiently.

        Future enhancement for performance optimization when processing
        large XLSX files with hundreds of campaigns.

        Args:
            value_strings: List of European decimal format strings

        Returns:
            list[float]: List of converted decimal values
        """
        results = []
        for value_string in value_strings:
            results.append(DataConverter.convert_european_decimal(value_string))
        return results


# Convenience functions for common operations
def convert_budget_eur(budget_string: str) -> float:
    """
    Convert European budget format to float with business validation.

    Wrapper function for common budget conversion with validation.
    """
    value = DataConverter.convert_european_decimal(budget_string)
    DataConverter.validate_numeric_range(value, 0.0, float('inf'))
    return value


def convert_cpm_eur(cpm_string: str) -> float:
    """
    Convert European CPM format to float with business validation.

    Wrapper function for CPM conversion with validation.
    """
    value = DataConverter.convert_european_decimal(cpm_string)
    DataConverter.validate_numeric_range(value, 0.0, float('inf'))
    return value