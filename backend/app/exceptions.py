"""
Unified Exception Hierarchy for PPV System Health Monitor

This module provides a structured exception hierarchy that enables:
1. Consistent error handling across all services
2. Structured error information with error codes and details
3. Backward compatibility during incremental migration
4. Business rule separation from technical errors
5. Monitoring and debugging support through structured error context

Educational Focus: Shows how a unified exception hierarchy improves
maintainability, debugging, and error handling consistency.

Key Design Patterns:
- Base exception with structured error information
- Error code generation for programmatic handling
- Details dictionary for debugging context
- Backward compatibility aliases for safe migration
"""

from datetime import datetime
from typing import Optional, Dict, Any
import threading


class PPVBaseException(Exception):
    """
    Base exception for all PPV System Health Monitor errors.

    Provides structured error handling with:
    - Automatic timestamp generation for error tracking
    - Error codes for programmatic error handling
    - Details dictionary for debugging context
    - Service identification for error origin tracking

    This base class enables consistent error handling patterns
    across all services while preserving backward compatibility.
    """

    # Class-level counter for unique error code generation
    _error_counter = 0
    _counter_lock = threading.Lock()

    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        """
        Initialize structured exception with error context.

        Args:
            message: Human-readable error description
            error_code: Unique error identifier (auto-generated if not provided)
            details: Dictionary containing error context for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._generate_error_code()
        self.details = details or {}
        self.timestamp = datetime.utcnow()

    def _generate_error_code(self) -> str:
        """
        Generate unique error code for this exception type.

        Override in subclasses to provide specific error code patterns.
        Base implementation provides generic PPV_BASE codes.
        """
        with PPVBaseException._counter_lock:
            PPVBaseException._error_counter += 1
            return f"PPV_BASE_{PPVBaseException._error_counter:03d}"

    def get_service(self) -> Optional[str]:
        """
        Extract service name from error details.

        Returns:
            Service name if specified in details, None otherwise
        """
        return self.details.get("service")

    def get_context(self) -> Dict[str, Any]:
        """
        Get complete error context dictionary.

        Returns:
            Dictionary containing all error context information
        """
        return self.details.copy()

    def is_business_rule_violation(self) -> bool:
        """
        Determine if this error represents a business rule violation.

        Returns:
            True if error details indicate business rule violation
        """
        return self.details.get("business_rule") is not None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for API responses or logging.

        Returns:
            Dictionary representation of exception with all context
        """
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "type": self.__class__.__name__
        }


class DataValidationError(PPVBaseException):
    """
    Data validation and conversion errors.

    Replaces ConversionError with structured error handling.
    Used for:
    - European decimal format conversion errors
    - Impression goal validation errors
    - Data type conversion failures
    - Input format validation errors

    Migration Target: ConversionError → DataValidationError
    """

    # Class-level counter for data validation error codes
    _data_error_counter = 0

    def _generate_error_code(self) -> str:
        """
        Generate PPV_DATA error codes for data validation errors.

        Pattern: PPV_DATA_001, PPV_DATA_002, etc.
        """
        with PPVBaseException._counter_lock:
            DataValidationError._data_error_counter += 1
            return f"PPV_DATA_{DataValidationError._data_error_counter:03d}"


class RuntimeParsingError(PPVBaseException):
    """
    Runtime parsing and date processing errors.

    Replaces RuntimeParseError with structured error handling.
    Used for:
    - Invalid runtime format errors
    - Date parsing failures
    - Pattern matching errors
    - Date validation errors

    Migration Target: RuntimeParseError → RuntimeParsingError
    """

    # Class-level counter for runtime parsing error codes
    _runtime_error_counter = 0

    def _generate_error_code(self) -> str:
        """
        Generate PPV_RUNTIME error codes for runtime parsing errors.

        Pattern: PPV_RUNTIME_001, PPV_RUNTIME_002, etc.
        """
        with PPVBaseException._counter_lock:
            RuntimeParsingError._runtime_error_counter += 1
            return f"PPV_RUNTIME_{RuntimeParsingError._runtime_error_counter:03d}"


class BusinessRuleError(PPVBaseException):
    """
    Business rule and constraint violations.

    Selective replacement for ValueError when error represents
    business logic violation rather than technical error.

    Used for:
    - Range validation errors (impression goals, budget limits)
    - Date logic violations (end before start)
    - System constraint violations
    - Business policy violations

    Migration Strategy: Only business rule ValueError → BusinessRuleError
    Technical ValueError instances remain as ValueError
    """

    # Class-level counter for business rule error codes
    _business_error_counter = 0

    def _generate_error_code(self) -> str:
        """
        Generate PPV_BUSINESS error codes for business rule violations.

        Pattern: PPV_BUSINESS_001, PPV_BUSINESS_002, etc.
        """
        with PPVBaseException._counter_lock:
            BusinessRuleError._business_error_counter += 1
            return f"PPV_BUSINESS_{BusinessRuleError._business_error_counter:03d}"

    def is_business_rule_violation(self) -> bool:
        """
        Business rule errors are always business rule violations.

        Returns:
            Always True for BusinessRuleError instances
        """
        return True


# =============================================================================
# Backward Compatibility Aliases
# =============================================================================

# Enable seamless migration from old exception types to new hierarchy
# These aliases ensure existing code continues working during incremental migration

# DataConverter migration: ConversionError → DataValidationError
ConversionError = DataValidationError

# RuntimeParser migration: RuntimeParseError → RuntimeParsingError
RuntimeParseError = RuntimeParsingError


# =============================================================================
# Convenience Functions for Exception Creation
# =============================================================================

def create_data_validation_error(
    message: str,
    service: str = None,
    input_value: Any = None,
    validation_context: str = None
) -> DataValidationError:
    """
    Convenience function for creating structured data validation errors.

    Args:
        message: Error description
        service: Service name where error occurred
        input_value: Input that caused the error
        validation_context: Context describing what validation failed

    Returns:
        DataValidationError with structured details
    """
    details = {}
    if service:
        details["service"] = service
    if input_value is not None:
        details["input_value"] = str(input_value)
    if validation_context:
        details["validation_context"] = validation_context

    return DataValidationError(message, details=details)


def create_runtime_parsing_error(
    message: str,
    input_runtime: str = None,
    expected_patterns: list = None
) -> RuntimeParsingError:
    """
    Convenience function for creating structured runtime parsing errors.

    Args:
        message: Error description
        input_runtime: Runtime string that failed parsing
        expected_patterns: List of expected runtime patterns

    Returns:
        RuntimeParsingError with structured details
    """
    details = {}
    if input_runtime:
        details["input_runtime"] = input_runtime
    if expected_patterns:
        details["expected_patterns"] = expected_patterns

    return RuntimeParsingError(message, details=details)


def create_business_rule_error(
    message: str,
    rule: str = None,
    provided_value: Any = None,
    limit: Any = None,
    business_context: str = None
) -> BusinessRuleError:
    """
    Convenience function for creating structured business rule errors.

    Args:
        message: Error description
        rule: Business rule identifier
        provided_value: Value that violated the rule
        limit: Rule limit or constraint
        business_context: Business context explaining the rule

    Returns:
        BusinessRuleError with structured details
    """
    details = {"business_rule": rule or "unknown"}
    if provided_value is not None:
        details["provided_value"] = provided_value
    if limit is not None:
        details["limit"] = limit
    if business_context:
        details["business_context"] = business_context

    return BusinessRuleError(message, details=details)