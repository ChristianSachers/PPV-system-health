"""
Business rule constants for campaign data foundation system.

This module centralizes business logic constants to eliminate hardcoded strings
and ensure consistency across the application.
"""

from typing import Any


class BusinessConstantsMeta(type):
    """Metaclass to protect class attributes from modification."""
    def __setattr__(cls, name: str, value: Any) -> None:
        if hasattr(cls, name) and name.isupper():
            raise AttributeError(f"Cannot modify business constant '{name}'")
        super().__setattr__(name, value)


class BusinessConstants(metaclass=BusinessConstantsMeta):
    """
    Central location for business rule constants.

    This class provides centralized access to business rule constants and helper
    methods for consistent campaign vs deal classification throughout the application.
    """

    # Campaign/Deal Classification Constants
    CAMPAIGN_BUYER_VALUE = "Not set"

    @classmethod
    def is_campaign_buyer(cls, buyer: Any) -> bool:
        """
        Check if buyer value indicates a campaign entity.

        Business Rule: Campaigns are identified by buyer="Not set" (exact match).
        Any other value indicates a deal entity.

        Args:
            buyer: The buyer value to check (typically string, but handles any type)

        Returns:
            bool: True if buyer indicates campaign entity, False otherwise

        Examples:
            >>> BusinessConstants.is_campaign_buyer("Not set")
            True
            >>> BusinessConstants.is_campaign_buyer("DENTSU_AEGIS < Easymedia_rtb")
            False
            >>> BusinessConstants.is_campaign_buyer(None)
            False
        """
        # Handle None explicitly
        if buyer is None:
            return False

        # Convert non-strings to strings for defensive programming
        if not isinstance(buyer, str):
            try:
                buyer_str = str(buyer)
            except (ValueError, TypeError):
                return False
        else:
            buyer_str = buyer

        # Exact string match required (case-sensitive, no whitespace normalization)
        return buyer_str == cls.CAMPAIGN_BUYER_VALUE