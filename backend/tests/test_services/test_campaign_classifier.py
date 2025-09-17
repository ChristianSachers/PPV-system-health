"""
Campaign Classifier Service TDD Template - Discovery-Driven Classification Testing

This template demonstrates:
1. Binary classification testing (Campaign vs Deal)
2. Edge case discovery through boundary testing
3. Business rule evolution through hypothesis testing
4. Safe experimentation with classification criteria

Educational Focus: Shows how to use TDD for discovering and validating
business classification rules where criteria might evolve during development.
"""

import pytest
from typing import Dict, Any, List

# Import your fixtures
from ..fixtures.campaign_test_data import CampaignClassificationData

# Real service imports - now implemented!
from app.services.campaign_classifier import CampaignClassifier, ClassificationResult, ClassificationError


# =============================================================================
# DISCOVERY TDD PATTERN 1: Binary Classification Hypothesis Testing
# =============================================================================

@pytest.mark.classification
class TestCampaignClassificationDiscovery:
    """
    Discovery TDD Approach: Test hypotheses about campaign vs deal classification

    Business Discovery: We're learning that buyer="Not set" indicates campaigns,
    while actual buyer strings indicate deals. This might evolve as we learn more.
    """

    def setup_method(self):
        """Setup for each test - backend-engineer will inject real service"""
        self.classifier = CampaignClassifier()

    @pytest.mark.parametrize("test_case", CampaignClassificationData.CAMPAIGNS)
    def test_campaign_classification_hypothesis(self, test_case):
        """
        HYPOTHESIS: buyer="Not set" (exact match) should classify as campaign

        Discovery Question: What makes something a campaign vs a deal?
        Business Rule: Campaigns don't have assigned buyers yet
        Evolution: This rule might become more complex as we discover edge cases
        """
        # ARRANGE - Use excellent test fixtures
        buyer = test_case["buyer"]
        expected_type = test_case["expected_type"]

        # ACT - Green phase: test actual implementation
        result = self.classifier.classify(buyer)

        # ASSERT - Validate classification behavior
        assert result.campaign_type == expected_type
        assert result.confidence > 0.5  # Should be confident in classification

        # Learning Documentation
        print(f"Learning: {test_case['description']} -> {expected_type}")

    @pytest.mark.parametrize("test_case", CampaignClassificationData.DEALS)
    def test_deal_classification_hypothesis(self, test_case):
        """
        HYPOTHESIS: Non-empty buyer strings should classify as deals

        Discovery Pattern: Test various buyer string formats we've observed
        Learning Goal: Understand what constitutes a valid deal buyer string
        """
        # ARRANGE
        buyer = test_case["buyer"]
        expected_type = test_case["expected_type"]

        # ACT - Green phase: test actual implementation
        result = self.classifier.classify(buyer)

        # ASSERT - Validate classification behavior
        assert result.campaign_type == expected_type

        print(f"Learning: {test_case['description']} -> {expected_type}")


# =============================================================================
# DISCOVERY TDD PATTERN 2: Edge Case and Boundary Discovery
# =============================================================================

@pytest.mark.classification
class TestClassificationBoundaryDiscovery:
    """
    Discovery TDD: Explore edge cases and boundary conditions

    These tests help us discover how the system should behave
    with unexpected or boundary case inputs.
    """

    def setup_method(self):
        self.classifier = CampaignClassifier()

    def test_case_sensitivity_boundary(self):
        """
        DISCOVERY TEST: How sensitive should classification be to case?

        Hypothesis: Only exact "Not set" should be campaign
        Learning: Case sensitivity is a business decision we're testing
        """
        test_cases = [
            {"buyer": "Not set", "expected": "campaign", "reason": "Exact match"},
            {"buyer": "not set", "expected": "deal", "reason": "Case sensitivity"},
            {"buyer": "Not Set", "expected": "deal", "reason": "Case sensitivity"},
            {"buyer": "NOT SET", "expected": "deal", "reason": "Case sensitivity"}
        ]

        for case in test_cases:
            # Red phase: test our hypothesis
            with pytest.raises(NotImplementedError):
                result = self.classifier.classify(case["buyer"])

            # Expected: assert result.campaign_type == case["expected"]
            print(f"Learning: '{case['buyer']}' -> {case['expected']} ({case['reason']})")

    def test_whitespace_handling_discovery(self):
        """
        DISCOVERY TEST: How should we handle whitespace in buyer strings?

        Business Question: Should "  Not set  " be treated as campaign?
        Discovery Pattern: Test whitespace edge cases
        """
        whitespace_cases = [
            {"buyer": "   Not set   ", "expected": "deal", "reason": "Whitespace breaks exact match"},
            {"buyer": "\tNot set\t", "expected": "deal", "reason": "Tab characters"},
            {"buyer": "\nNot set\n", "expected": "deal", "reason": "Newline characters"},
            {"buyer": "", "expected": "unknown", "reason": "Empty string needs handling"}
        ]

        for case in whitespace_cases:
            with pytest.raises(NotImplementedError):
                result = self.classifier.classify(case["buyer"])

            print(f"Learning: Whitespace test '{repr(case['buyer'])}' -> {case['expected']}")

    def test_null_and_none_handling_discovery(self):
        """
        DISCOVERY TEST: How should we handle None or null buyer values?

        Edge Case Discovery: What if buyer field is missing from data?
        """
        edge_cases = [
            {"buyer": None, "expected_error": ClassificationError, "reason": "None buyer should error"},
            # We might discover more edge cases during implementation
        ]

        for case in edge_cases:
            with pytest.raises(case["expected_error"]):
                result = self.classifier.classify(case["buyer"])

            print(f"Learning: {case['reason']}")


# =============================================================================
# DISCOVERY TDD PATTERN 3: Business Rule Evolution Testing
# =============================================================================

@pytest.mark.classification
@pytest.mark.discovery
class TestClassificationRuleEvolution:
    """
    Discovery TDD: Tests that can evolve as business rules become clearer

    These tests document our current understanding but are designed
    to be easily modified as we discover new classification patterns.
    """

    def setup_method(self):
        self.classifier = CampaignClassifier()

    def test_complex_buyer_string_patterns(self):
        """
        DISCOVERY TEST: Learn from real buyer string patterns

        As we process more data, we might discover new patterns
        that require classification rule updates.
        """
        # Pattern discovered: buyer strings with angle brackets and seat IDs
        complex_patterns = [
            {
                "buyer": "DENTSU_AEGIS < Easymedia_rtb (Seat 608194)",
                "expected": "deal",
                "pattern": "company_name < platform_name (Seat ID)"
            },
            {
                "buyer": "AMAZON_DSP < Amazon_DSP (Seat 123456)",
                "expected": "deal",
                "pattern": "DSP_name < DSP_name (Seat ID)"
            },
            # We might discover more patterns and need to update this test
        ]

        for pattern in complex_patterns:
            with pytest.raises(NotImplementedError):
                result = self.classifier.classify(pattern["buyer"])

            # Expected: assert result.campaign_type == pattern["expected"]
            print(f"Learning: Pattern '{pattern['pattern']}' -> {pattern['expected']}")

    def test_classification_confidence_hypothesis(self):
        """
        DISCOVERY TEST: Should classifier provide confidence scores?

        Future Enhancement: We might want confidence scores for classifications
        This test prepares for that possibility
        """
        test_buyer = "DENTSU_AEGIS < Easymedia_rtb (Seat 608194)"

        with pytest.raises(NotImplementedError):
            result = self.classifier.classify(test_buyer)

        # Future assertion: assert result.confidence >= 0.8
        # High confidence for clear deal pattern

        print("Learning: Confidence scoring might be valuable for unclear cases")

    def test_reasoning_explanation_discovery(self):
        """
        DISCOVERY TEST: Should classifier explain its reasoning?

        Explainability: For complex business rules, explanations help validation
        """
        with pytest.raises(NotImplementedError):
            result = self.classifier.classify("Not set")

        # Future expectation:
        # assert "exact match" in result.reasoning.lower()

        print("Learning: Reasoning explanations could help business validation")


# =============================================================================
# DISCOVERY TDD PATTERN 4: Integration with Real Data
# =============================================================================

@pytest.mark.classification
@pytest.mark.integration
class TestClassificationIntegrationDiscovery:
    """
    Discovery TDD: Test classification with complete campaign data

    Integration tests using your excellent comprehensive fixtures.
    """

    def test_complete_campaign_classification(self, sample_campaigns):
        """
        INTEGRATION TEST: Classify all campaigns from our sample data

        Discovery Goal: Ensure classifier works with real campaign records
        Validation: Check that classifications match expected business rules
        """
        classifier = CampaignClassifier()

        for campaign in sample_campaigns:
            buyer = campaign["buyer"]
            expected_type = campaign["expected_type"]

            # Red phase: integration test will fail until implemented
            with pytest.raises(NotImplementedError):
                result = classifier.classify(buyer)

            # Expected integration behavior:
            # result = classifier.classify(buyer)
            # assert result.campaign_type == expected_type

            print(f"Learning: Campaign '{campaign['name']}' buyer '{buyer}' -> {expected_type}")

    def test_batch_classification_performance_discovery(self, sample_campaigns):
        """
        DISCOVERY TEST: How should we handle batch classification?

        Performance Consideration: Can we classify multiple campaigns efficiently?
        Future Enhancement: Batch processing might be needed for large datasets
        """
        classifier = CampaignClassifier()
        buyers = [campaign["buyer"] for campaign in sample_campaigns]

        # Future batch method test:
        # results = classifier.classify_batch(buyers)
        # assert len(results) == len(buyers)

        print(f"Learning: Batch processing for {len(buyers)} campaigns might be needed")


# =============================================================================
# TDD GUIDANCE FOR BACKEND-ENGINEER
# =============================================================================

"""
IMPLEMENTATION GUIDANCE FOR BACKEND-ENGINEER:

1. RED PHASE (Current State):
   - All tests fail with NotImplementedError
   - This documents our classification hypotheses

2. GREEN PHASE (Implementation Steps):
   - Start with simple exact match: buyer == "Not set" -> campaign
   - Then handle all other cases as deals
   - Add error handling for None/empty buyers

3. REFACTOR PHASE:
   - Extract classification rules into configurable patterns
   - Add confidence scoring if needed
   - Consider performance optimizations

DISCOVERY TDD APPROACH:
- Start with the simplest rule (exact "Not set" match)
- Test edge cases to understand boundaries
- Consider future enhancements (confidence, reasoning, batch processing)

EXAMPLE IMPLEMENTATION SKELETON:

class CampaignClassifier:
    def classify(self, buyer: str) -> ClassificationResult:
        if buyer is None:
            raise ValueError("Buyer cannot be None")

        if buyer == "Not set":  # Exact match only
            return ClassificationResult(
                campaign_type="campaign",
                confidence=1.0,
                reasoning="Exact match for 'Not set' indicates campaign"
            )
        elif buyer.strip():  # Non-empty after stripping
            return ClassificationResult(
                campaign_type="deal",
                confidence=1.0,
                reasoning="Non-empty buyer string indicates deal"
            )
        else:
            raise ValueError("Buyer cannot be empty string")

TESTING COMMANDS:
- Run: pytest tests/test_services/test_campaign_classifier.py -v
- Watch the Red-Green-Refactor cycle
- Use parametrized tests to validate all edge cases

EVOLUTION STRATEGY:
- As business rules become clearer, update the classification logic
- Tests are designed to be easily modified for new patterns
- Consider adding new classification categories if discovered
"""