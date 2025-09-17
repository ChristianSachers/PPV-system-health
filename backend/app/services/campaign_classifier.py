"""
CampaignClassifier Service - Campaign vs Deal Classification

This service handles the binary classification logic for campaign data:
1. Campaign classification: buyer = "Not set" (exact match, case-sensitive)
2. Deal classification: Any other buyer string (non-empty actual buyers)
3. Edge case handling: Empty strings, None values, whitespace variations
4. Business rule validation and confidence scoring

Key Business Rules:
- Campaigns: buyer field is exactly "Not set" (case-sensitive)
- Deals: buyer field contains actual buyer information (DSP names, seat IDs, etc.)
- Case sensitivity: Only exact "Not set" qualifies as campaign
- Whitespace sensitivity: " Not set " (with spaces) is considered a deal
"""

from typing import Dict, Any, Optional
from enum import Enum


class CampaignType(Enum):
    """Enumeration of campaign classification types"""
    CAMPAIGN = "campaign"
    DEAL = "deal"


class ClassificationError(Exception):
    """Custom exception for classification errors"""
    pass


class ClassificationResult:
    """Result class containing classification details and confidence"""
    def __init__(self, campaign_type: str, confidence: float = 1.0, reasoning: str = ""):
        self.campaign_type = campaign_type
        self.confidence = confidence
        self.reasoning = reasoning

    def to_dict(self) -> Dict[str, Any]:
        """Convert classification result to dictionary for database storage"""
        return {
            'campaign_type': self.campaign_type,
            'confidence': self.confidence,
            'reasoning': self.reasoning
        }


class CampaignClassifier:
    """
    Service for classifying campaign data as either campaigns or deals.

    The classification is based on the buyer field with a simple but critical rule:
    - Campaigns: buyer = "Not set" (exact match)
    - Deals: buyer = any other string (actual buyer information)

    This binary classification drives fulfillment analysis categorization.
    """

    # Business rule constants
    CAMPAIGN_BUYER_VALUE = "Not set"

    @staticmethod
    def classify(buyer: str) -> ClassificationResult:
        """
        Classify campaign data as campaign or deal based on buyer field.

        Business Rule:
        - Campaign: buyer field is exactly "Not set" (case-sensitive)
        - Deal: buyer field contains any other value

        Args:
            buyer: Buyer field value from campaign data

        Returns:
            ClassificationResult: Classification with type, confidence, and reasoning

        Raises:
            TypeError: If buyer is not a string
            ClassificationError: If buyer is None or invalid

        Examples:
            >>> CampaignClassifier.classify("Not set")
            ClassificationResult(campaign_type="campaign", confidence=1.0)

            >>> CampaignClassifier.classify("DENTSU_AEGIS < Easymedia_rtb (Seat 608194)")
            ClassificationResult(campaign_type="deal", confidence=1.0)
        """
        if buyer is None:
            raise ClassificationError("Buyer field cannot be None")

        if not isinstance(buyer, str):
            raise TypeError("Buyer field must be a string")

        # Business rule: Exact match for "Not set" indicates campaign
        if buyer == CampaignClassifier.CAMPAIGN_BUYER_VALUE:
            return ClassificationResult(
                campaign_type=CampaignType.CAMPAIGN.value,
                confidence=1.0,
                reasoning=f"Exact match: buyer = '{CampaignClassifier.CAMPAIGN_BUYER_VALUE}'"
            )

        # All other values (including case variations, whitespace, etc.) are deals
        return ClassificationResult(
            campaign_type=CampaignType.DEAL.value,
            confidence=1.0,
            reasoning=f"Non-campaign buyer: '{buyer}'"
        )

    @staticmethod
    def is_campaign(buyer: str) -> bool:
        """
        Quick check if buyer indicates a campaign.

        Convenience method for simple boolean classification.

        Args:
            buyer: Buyer field value

        Returns:
            bool: True if classified as campaign, False if deal
        """
        try:
            result = CampaignClassifier.classify(buyer)
            return result.campaign_type == CampaignType.CAMPAIGN.value
        except (TypeError, ClassificationError):
            return False

    @staticmethod
    def is_deal(buyer: str) -> bool:
        """
        Quick check if buyer indicates a deal.

        Convenience method for simple boolean classification.

        Args:
            buyer: Buyer field value

        Returns:
            bool: True if classified as deal, False if campaign
        """
        return not CampaignClassifier.is_campaign(buyer)

    @staticmethod
    def get_classification_reasoning(buyer: str) -> str:
        """
        Get detailed reasoning for classification decision.

        Useful for debugging and business rule validation.

        Args:
            buyer: Buyer field value

        Returns:
            str: Human-readable reasoning for classification
        """
        try:
            result = CampaignClassifier.classify(buyer)
            return result.reasoning
        except (TypeError, ClassificationError) as e:
            return f"Classification error: {e}"

    @staticmethod
    def validate_buyer_format(buyer: str) -> bool:
        """
        Validate that buyer field has acceptable format.

        Currently accepts any non-empty string, but could be extended
        for more sophisticated validation rules.

        Args:
            buyer: Buyer field value

        Returns:
            bool: True if format is valid
        """
        if not isinstance(buyer, str):
            return False

        # Empty strings are technically valid (will be classified as deals)
        # but might indicate data quality issues
        return True

    @staticmethod
    def get_campaign_statistics(buyer_list: list[str]) -> Dict[str, Any]:
        """
        Generate classification statistics for a list of buyers.

        Useful for analyzing campaign vs deal distribution in datasets.

        Args:
            buyer_list: List of buyer field values

        Returns:
            Dict[str, Any]: Statistics including counts, percentages, and invalid entries
        """
        if not buyer_list:
            return {
                'total_count': 0,
                'campaign_count': 0,
                'deal_count': 0,
                'campaign_percentage': 0.0,
                'deal_percentage': 0.0,
                'invalid_count': 0
            }

        campaign_count = 0
        deal_count = 0
        invalid_count = 0

        for buyer in buyer_list:
            try:
                if CampaignClassifier.is_campaign(buyer):
                    campaign_count += 1
                else:
                    deal_count += 1
            except (TypeError, ClassificationError):
                invalid_count += 1

        total_valid = campaign_count + deal_count
        total_count = len(buyer_list)

        return {
            'total_count': total_count,
            'campaign_count': campaign_count,
            'deal_count': deal_count,
            'campaign_percentage': (campaign_count / total_valid * 100) if total_valid > 0 else 0.0,
            'deal_percentage': (deal_count / total_valid * 100) if total_valid > 0 else 0.0,
            'invalid_count': invalid_count
        }


# Convenience functions for common operations
def classify_buyer(buyer: str) -> str:
    """
    Simple classification function that returns campaign type as string.

    Wrapper function for easy integration with existing code.
    """
    result = CampaignClassifier.classify(buyer)
    return result.campaign_type


def is_campaign_buyer(buyer: str) -> bool:
    """
    Check if buyer indicates a campaign.

    Wrapper function for boolean classification checks.
    """
    return CampaignClassifier.is_campaign(buyer)