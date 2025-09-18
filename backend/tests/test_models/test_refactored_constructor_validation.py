"""
Refactored Constructor Validation Tests

This file validates that the refactored constructor produces identical
behavior to the current constructor. These tests ensure no behavior
changes during the refactoring process.

Educational Focus: How to validate constructor refactoring using
direct behavior comparison tests.
"""

import pytest
from datetime import date, datetime
from uuid import uuid4

# Import both current and refactored implementations
from app.models.campaign import Campaign
from app.models.campaign_refactored_constructor import RefactoredCampaignConstructor


# =============================================================================
# REFACTORED CONSTRUCTOR BEHAVIOR VALIDATION
# =============================================================================

class TestRefactoredConstructorValidation:
    """
    Test that refactored constructor produces identical behavior.

    These tests create campaigns using both current and refactored
    constructors and verify they produce identical results.
    """

    def test_identical_behavior_valid_campaign_data(self, test_db_session):
        """Test that refactored constructor produces identical results for valid data"""
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
        current_campaign = Campaign(**campaign_data)
        test_db_session.add(current_campaign)
        test_db_session.commit()

        # Create campaign with refactored constructor (simulated)
        # Note: This creates a temporary Campaign instance for comparison
        refactored_campaign = Campaign.__new__(Campaign)
        RefactoredCampaignConstructor.refactored_init(refactored_campaign, **campaign_data)

        # Verify identical behavior
        assert current_campaign.id == refactored_campaign.id
        assert current_campaign.name == refactored_campaign.name
        assert current_campaign.runtime_start == refactored_campaign.runtime_start
        assert current_campaign.runtime_end == refactored_campaign.runtime_end
        assert current_campaign.impression_goal == refactored_campaign.impression_goal
        assert current_campaign.budget_eur == refactored_campaign.budget_eur
        assert current_campaign.cpm_eur == refactored_campaign.cpm_eur
        assert current_campaign.buyer == refactored_campaign.buyer
        assert current_campaign.entity_type == refactored_campaign.entity_type
        assert current_campaign.is_running == refactored_campaign.is_running

        print("✅ Refactored constructor produces identical valid campaign behavior")

    def test_identical_behavior_asap_campaign(self, test_db_session):
        """Test identical behavior for ASAP campaigns"""
        campaign_data = {
            "id": str(uuid4()),
            "name": "ASAP Refactored Test",
            "runtime": "ASAP-30.06.2025",
            "impression_goal": 1000000,
            "budget_eur": 10000.0,
            "cpm_eur": 2.0,
            "buyer": "Not set"
        }

        # Current constructor
        current_campaign = Campaign(**campaign_data)
        test_db_session.add(current_campaign)
        test_db_session.commit()

        # Refactored constructor
        refactored_campaign = Campaign.__new__(Campaign)
        RefactoredCampaignConstructor.refactored_init(refactored_campaign, **campaign_data)

        # Verify ASAP behavior is identical
        assert current_campaign.runtime_start is None
        assert refactored_campaign.runtime_start is None
        assert current_campaign.runtime_end.date() == refactored_campaign.runtime_end.date()
        assert current_campaign.entity_type == refactored_campaign.entity_type  # "campaign"
        assert current_campaign.is_running == refactored_campaign.is_running

        print("✅ Refactored constructor produces identical ASAP campaign behavior")

    def test_identical_error_messages_invalid_uuid(self):
        """Test that error messages are identical for invalid UUID"""
        campaign_data = {
            "id": "invalid-uuid",
            "name": "Error Test",
            "runtime": "ASAP-30.06.2025",
            "impression_goal": 1000000,
            "budget_eur": 10000.0,
            "cpm_eur": 2.0,
            "buyer": "Not set"
        }

        # Current constructor error
        current_error = None
        try:
            Campaign(**campaign_data)
        except ValueError as e:
            current_error = str(e)

        # Refactored constructor error
        refactored_error = None
        try:
            refactored_campaign = Campaign.__new__(Campaign)
            RefactoredCampaignConstructor.refactored_init(refactored_campaign, **campaign_data)
        except ValueError as e:
            refactored_error = str(e)

        # Verify identical error messages
        assert current_error is not None
        assert refactored_error is not None
        assert current_error == refactored_error

        print(f"✅ Identical error messages: {current_error}")

    def test_identical_error_messages_negative_budget(self):
        """Test identical error messages for negative budget"""
        campaign_data = {
            "id": str(uuid4()),
            "name": "Negative Budget Test",
            "runtime": "ASAP-30.06.2025",
            "impression_goal": 1000000,
            "budget_eur": -1000.0,  # Invalid
            "cpm_eur": 2.0,
            "buyer": "Not set"
        }

        # Compare error messages
        current_error = None
        try:
            Campaign(**campaign_data)
        except ValueError as e:
            current_error = str(e)

        refactored_error = None
        try:
            refactored_campaign = Campaign.__new__(Campaign)
            RefactoredCampaignConstructor.refactored_init(refactored_campaign, **campaign_data)
        except ValueError as e:
            refactored_error = str(e)

        assert current_error == refactored_error
        print(f"✅ Identical negative budget error: {current_error}")

    def test_identical_error_messages_empty_name(self):
        """Test identical error messages for empty campaign name"""
        campaign_data = {
            "id": str(uuid4()),
            "name": "",  # Invalid
            "runtime": "ASAP-30.06.2025",
            "impression_goal": 1000000,
            "budget_eur": 10000.0,
            "cpm_eur": 2.0,
            "buyer": "Not set"
        }

        # Compare error messages
        current_error = None
        try:
            Campaign(**campaign_data)
        except ValueError as e:
            current_error = str(e)

        refactored_error = None
        try:
            refactored_campaign = Campaign.__new__(Campaign)
            RefactoredCampaignConstructor.refactored_init(refactored_campaign, **campaign_data)
        except ValueError as e:
            refactored_error = str(e)

        assert current_error == refactored_error
        print(f"✅ Identical empty name error: {current_error}")

    def test_identical_field_correction_behavior(self, test_db_session):
        """Test that field corrections work identically"""
        campaign_data = {
            "id": str(uuid4()),
            "name": "Field Correction Test",
            "runtime": "ASAP-30.06.2025",
            "impression_goal": 1000000,
            "budget_eur": 10000.0,
            "cmp_eur": 2.5,  # Typo: should become cpm_eur
            "buyer": "Not set"
        }

        # Current constructor (handles cmp_eur -> cpm_eur correction)
        current_campaign = Campaign(**campaign_data)
        test_db_session.add(current_campaign)
        test_db_session.commit()

        # Refactored constructor (should handle same correction)
        refactored_campaign = Campaign.__new__(Campaign)
        RefactoredCampaignConstructor.refactored_init(refactored_campaign, **campaign_data)

        # Verify field correction worked identically
        assert current_campaign.cpm_eur == 2.5
        assert refactored_campaign.cpm_eur == 2.5
        assert not hasattr(current_campaign, 'cmp_eur')
        assert not hasattr(refactored_campaign, 'cmp_eur')

        print("✅ Identical field correction behavior")

    def test_identical_runtime_parsing_behavior(self, test_db_session):
        """Test that runtime parsing behavior is identical"""
        test_cases = [
            {
                "runtime": "ASAP-30.06.2025",
                "expected_start": None,
                "expected_end_date": date(2025, 6, 30)
            },
            {
                "runtime": "07.07.2025-24.07.2025",
                "expected_start_date": date(2025, 7, 7),
                "expected_end_date": date(2025, 7, 24)
            }
        ]

        for case in test_cases:
            campaign_data = {
                "id": str(uuid4()),
                "name": f"Runtime Test {case['runtime']}",
                "runtime": case["runtime"],
                "impression_goal": 1000000,
                "budget_eur": 10000.0,
                "cpm_eur": 2.0,
                "buyer": "Not set"
            }

            # Current constructor
            current_campaign = Campaign(**campaign_data)

            # Refactored constructor
            refactored_campaign = Campaign.__new__(Campaign)
            RefactoredCampaignConstructor.refactored_init(refactored_campaign, **campaign_data)

            # Verify identical runtime parsing
            if case["runtime"].startswith("ASAP"):
                assert current_campaign.runtime_start is None
                assert refactored_campaign.runtime_start is None
            else:
                assert current_campaign.runtime_start.date() == case["expected_start_date"]
                assert refactored_campaign.runtime_start.date() == case["expected_start_date"]

            assert current_campaign.runtime_end.date() == case["expected_end_date"]
            assert refactored_campaign.runtime_end.date() == case["expected_end_date"]

        print("✅ Identical runtime parsing behavior for all formats")


# =============================================================================
# PERFORMANCE COMPARISON TESTS
# =============================================================================

class TestRefactoredConstructorPerformance:
    """
    Test that refactored constructor doesn't significantly impact performance.

    These tests ensure the refactoring doesn't introduce performance regressions.
    """

    def test_performance_comparison(self, test_db_session):
        """Compare performance of current vs refactored constructor"""
        import time

        campaign_data = {
            "id": str(uuid4()),
            "name": "Performance Test Campaign",
            "runtime": "07.07.2025-24.07.2025",
            "impression_goal": 1500000,
            "budget_eur": 15000.75,
            "cpm_eur": 2.55,
            "buyer": "Performance Test Buyer"
        }

        # Time current constructor
        start_time = time.time()
        for _ in range(100):
            campaign = Campaign(**campaign_data)
            campaign_data["id"] = str(uuid4())  # Unique ID for each
        current_time = time.time() - start_time

        # Time refactored constructor
        start_time = time.time()
        for _ in range(100):
            refactored_campaign = Campaign.__new__(Campaign)
            RefactoredCampaignConstructor.refactored_init(refactored_campaign, **campaign_data)
            campaign_data["id"] = str(uuid4())  # Unique ID for each
        refactored_time = time.time() - start_time

        # Performance should be similar (within 50% difference)
        performance_ratio = refactored_time / current_time
        assert performance_ratio < 1.5, f"Refactored constructor is {performance_ratio:.2f}x slower"

        print(f"✅ Performance comparison: Current={current_time:.4f}s, Refactored={refactored_time:.4f}s")
        print(f"   Performance ratio: {performance_ratio:.2f}x")


# =============================================================================
# COMPREHENSIVE BEHAVIOR VALIDATION
# =============================================================================

"""
REFACTORED CONSTRUCTOR VALIDATION SUMMARY:
==========================================

These tests validate that the refactored constructor:

✅ Produces identical field values for valid data
✅ Produces identical error messages for invalid data
✅ Handles ASAP campaigns identically
✅ Handles field corrections identically
✅ Parses runtime strings identically
✅ Calculates completion status identically
✅ Maintains similar performance characteristics

SUCCESS CRITERIA FOR REFACTORING:
- All tests in this file pass
- All existing characterization tests pass
- All existing Campaign model tests pass
- Performance doesn't degrade significantly

If all criteria are met, the constructor refactoring is successful
and provides genuine value through better code organization while
maintaining exact backward compatibility.

NEXT STEPS:
1. Run these validation tests
2. Run all existing tests
3. If everything passes, integrate refactored constructor
4. If anything fails, analyze and fix before integration
"""