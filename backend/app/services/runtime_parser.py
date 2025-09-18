"""
RuntimeParser Service - Campaign Runtime Format Parsing

This service handles the complex runtime format parsing requirements for campaign data:
1. ASAP format parsing: "ASAP-30.06.2025" → start_date=None, end_date=date(2025,6,30)
2. Standard format parsing: "07.07.2025-24.07.2025" → start_date=date(2025,7,7), end_date=date(2025,7,24)
3. European date format handling: DD.MM.YYYY
4. Campaign completion status determination
5. Business rule validation for date ranges

Key Business Rules:
- ASAP campaigns: start_date is None (undefined start)
- Standard campaigns: both start_date and end_date are defined
- End date must be after start date (when both defined)
- Date format is European: DD.MM.YYYY
- Campaign status: running vs completed based on current date
"""

import re
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple

# Import unified exception hierarchy
from app.exceptions import RuntimeParsingError, BusinessRuleError


class RuntimeParseError(Exception):
    """Custom exception for runtime parsing errors"""
    pass


class ParseResult:
    """Result class containing parsed runtime information"""
    def __init__(self, start_date: Optional[date], end_date: date, is_running: bool = True):
        self.start_date = start_date
        self.end_date = end_date
        self.is_running = is_running

    def to_dict(self) -> Dict[str, Any]:
        """Convert parse result to dictionary for database storage"""
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_running': self.is_running
        }


class RuntimeParser:
    """
    Service for parsing campaign runtime strings into structured date information.

    Handles two primary runtime formats found in campaign data:
    1. ASAP Format: "ASAP-30.06.2025" (start immediately, end on specified date)
    2. Standard Format: "07.07.2025-24.07.2025" (defined start and end dates)

    European date format (DD.MM.YYYY) is used throughout.
    """

    # Regex patterns for runtime format detection
    ASAP_PATTERN = re.compile(r'^ASAP-(\d{2})\.(\d{2})\.(\d{4})$')
    STANDARD_PATTERN = re.compile(r'^(\d{2})\.(\d{2})\.(\d{4})-(\d{2})\.(\d{2})\.(\d{4})$')

    @staticmethod
    def parse(runtime_string: str, current_date: Optional[date] = None) -> ParseResult:
        """
        Parse runtime string into structured date information.

        Args:
            runtime_string: Runtime format string from XLSX
            current_date: Current date for status calculation (defaults to today)

        Returns:
            ParseResult: Parsed runtime information with dates and status

        Raises:
            RuntimeParseError: If runtime string is invalid or malformed
            ValueError: If dates are invalid or violate business rules

        Examples:
            >>> RuntimeParser.parse("ASAP-30.06.2025")
            ParseResult(start_date=None, end_date=date(2025,6,30), is_running=True)

            >>> RuntimeParser.parse("07.07.2025-24.07.2025")
            ParseResult(start_date=date(2025,7,7), end_date=date(2025,7,24), is_running=True)
        """
        if not isinstance(runtime_string, str):
            raise TypeError("Runtime string must be a string")

        if not runtime_string.strip():
            raise RuntimeParsingError(
                "Runtime string cannot be empty",
                details={
                    "service": "RuntimeParser",
                    "method": "parse",
                    "input_value": runtime_string,
                    "validation_context": "empty_runtime_string"
                }
            )

        cleaned_runtime = runtime_string.strip()

        # Default current date to today if not provided
        if current_date is None:
            current_date = date.today()

        # Try ASAP format first
        asap_match = RuntimeParser.ASAP_PATTERN.match(cleaned_runtime)
        if asap_match:
            return RuntimeParser._parse_asap_format(asap_match, current_date)

        # Try standard format
        standard_match = RuntimeParser.STANDARD_PATTERN.match(cleaned_runtime)
        if standard_match:
            return RuntimeParser._parse_standard_format(standard_match, current_date)

        # No pattern matched
        raise RuntimeParsingError(
            f"Invalid runtime format: '{runtime_string}'. Expected 'ASAP-DD.MM.YYYY' or 'DD.MM.YYYY-DD.MM.YYYY'",
            details={
                "service": "RuntimeParser",
                "method": "parse",
                "input_value": runtime_string,
                "expected_patterns": ["ASAP-DD.MM.YYYY", "DD.MM.YYYY-DD.MM.YYYY"],
                "validation_context": "runtime_format_matching"
            }
        )

    @staticmethod
    def _parse_asap_format(match: re.Match, current_date: date) -> ParseResult:
        """
        Parse ASAP format: "ASAP-30.06.2025"

        ASAP means start_date = None (start as soon as possible)
        Only end_date is specified.
        """
        day, month, year = match.groups()

        try:
            end_date = RuntimeParser._create_date(int(day), int(month), int(year))
        except ValueError as e:
            raise RuntimeParsingError(
                f"Invalid end date in ASAP format: {e}",
                details={
                    "service": "RuntimeParser",
                    "method": "_parse_asap_format",
                    "input_value": f"{day}.{month}.{year}",
                    "validation_context": "ASAP_date_validation",
                    "original_error": str(e)
                }
            )

        # ASAP campaigns have no defined start date
        start_date = None

        # Determine if campaign is still running (end date is in future or today)
        is_running = end_date >= current_date

        return ParseResult(start_date=start_date, end_date=end_date, is_running=is_running)

    @staticmethod
    def _parse_standard_format(match: re.Match, current_date: date) -> ParseResult:
        """
        Parse standard format: "07.07.2025-24.07.2025"

        Both start_date and end_date are specified.
        Must validate that end_date > start_date.
        """
        start_day, start_month, start_year, end_day, end_month, end_year = match.groups()

        try:
            start_date = RuntimeParser._create_date(int(start_day), int(start_month), int(start_year))
            end_date = RuntimeParser._create_date(int(end_day), int(end_month), int(end_year))
        except ValueError as e:
            raise RuntimeParsingError(
                f"Invalid date in standard format: {e}",
                details={
                    "service": "RuntimeParser",
                    "method": "_parse_standard_format",
                    "input_value": f"{start_day}.{start_month}.{start_year}-{end_day}.{end_month}.{end_year}",
                    "validation_context": "standard_date_validation",
                    "original_error": str(e)
                }
            )

        # Business rule: end date must be after start date
        if end_date <= start_date:
            raise BusinessRuleError(
                f"End date {end_date} must be after start date {start_date}",
                details={
                    "service": "RuntimeParser",
                    "method": "_parse_standard_format",
                    "business_rule": "end_date_after_start_date",
                    "provided_start_date": str(start_date),
                    "provided_end_date": str(end_date),
                    "business_context": "campaign_date_logic"
                }
            )

        # Determine if campaign is still running (end date is in future or today)
        is_running = end_date >= current_date

        return ParseResult(start_date=start_date, end_date=end_date, is_running=is_running)

    @staticmethod
    def _create_date(day: int, month: int, year: int) -> date:
        """
        Create date object with validation.

        Raises ValueError for invalid dates (e.g., February 30, month 13, etc.)
        """
        try:
            return date(year, month, day)
        except ValueError as e:
            raise ValueError(f"Invalid date {day:02d}.{month:02d}.{year}: {e}")

    @staticmethod
    def is_campaign_completed(runtime_string: str, current_date: Optional[date] = None) -> bool:
        """
        Determine if a campaign is completed based on its runtime.

        Convenience method for business logic that needs to check completion status.

        Args:
            runtime_string: Runtime format string
            current_date: Date to check against (defaults to today)

        Returns:
            bool: True if campaign is completed (end_date < current_date)
        """
        try:
            result = RuntimeParser.parse(runtime_string, current_date)
            return not result.is_running
        except (RuntimeParseError, ValueError):
            # If parsing fails, assume campaign is not completed
            return False

    @staticmethod
    def extract_date_range(runtime_string: str) -> Tuple[Optional[date], date]:
        """
        Extract just the date range from runtime string.

        Convenience method that returns (start_date, end_date) tuple
        without status calculation.

        Returns:
            Tuple[Optional[date], date]: (start_date, end_date)
                start_date is None for ASAP format
        """
        result = RuntimeParser.parse(runtime_string)
        return (result.start_date, result.end_date)

    @staticmethod
    def validate_runtime_format(runtime_string: str) -> bool:
        """
        Validate runtime string format without full parsing.

        Quick validation for input validation scenarios.

        Returns:
            bool: True if format is valid (ASAP or standard format)
        """
        if not isinstance(runtime_string, str) or not runtime_string.strip():
            return False

        cleaned = runtime_string.strip()
        return (RuntimeParser.ASAP_PATTERN.match(cleaned) is not None or
                RuntimeParser.STANDARD_PATTERN.match(cleaned) is not None)

    @staticmethod
    def get_campaign_duration_days(runtime_string: str) -> Optional[int]:
        """
        Calculate campaign duration in days.

        For ASAP campaigns, returns None since start date is undefined.
        For standard campaigns, returns number of days between start and end.

        Returns:
            Optional[int]: Duration in days, or None for ASAP campaigns
        """
        try:
            result = RuntimeParser.parse(runtime_string)
            if result.start_date is None:
                return None  # ASAP campaigns have undefined duration

            duration = (result.end_date - result.start_date).days
            return duration + 1  # Include both start and end days
        except (RuntimeParseError, ValueError):
            return None


# Convenience functions for common operations
def parse_runtime(runtime_string: str) -> Dict[str, Any]:
    """
    Parse runtime string and return dictionary for database storage.

    Wrapper function for easy integration with ORM models.
    """
    result = RuntimeParser.parse(runtime_string)
    return result.to_dict()


def is_runtime_valid(runtime_string: str) -> bool:
    """
    Check if runtime string has valid format.

    Wrapper function for input validation.
    """
    return RuntimeParser.validate_runtime_format(runtime_string)