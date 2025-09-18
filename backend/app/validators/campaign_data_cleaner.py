"""
Campaign Data Cleaner - Data Quality and Field Correction Utilities

This module handles data cleaning and field corrections for campaign data.
It addresses known data quality issues and provides utilities for normalizing
campaign data from various sources (XLSX imports, API calls, etc.).

Educational Focus: How to encapsulate data quality logic separately from
business validation logic for better maintainability.
"""

from typing import Dict, Any
import copy


class CampaignDataCleaner:
    """
    Data cleaning utilities for campaign data.

    This class handles known data quality issues and field corrections
    that are specific to campaign data sources. It separates data cleaning
    concerns from business validation concerns.
    """

    @staticmethod
    def apply_field_corrections(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply known field corrections to campaign data.

        This method handles known data quality issues such as:
        - Field name typos (cmp_eur -> cpm_eur)
        - Field name variations from different data sources
        - Other systematic data quality issues

        Args:
            data: Dictionary of campaign data that may contain field issues

        Returns:
            Dict[str, Any]: Cleaned data dictionary with corrections applied

        Example:
            >>> cleaner = CampaignDataCleaner()
            >>> dirty_data = {"id": "123", "cmp_eur": 2.5}  # Typo: cmp_eur
            >>> clean_data = cleaner.apply_field_corrections(dirty_data)
            >>> assert clean_data["cpm_eur"] == 2.5
            >>> assert "cmp_eur" not in clean_data
        """
        # Create a copy to avoid modifying the original data
        cleaned_data = copy.deepcopy(data)

        # Field correction: cmp_eur -> cpm_eur (known typo in test data)
        if 'cmp_eur' in cleaned_data:
            # Move the value to the correct field name
            cleaned_data['cpm_eur'] = cleaned_data.pop('cmp_eur')

        # Future field corrections can be added here
        # Examples:
        # if 'campaignName' in cleaned_data:  # camelCase -> snake_case
        #     cleaned_data['campaign_name'] = cleaned_data.pop('campaignName')
        #
        # if 'impressions_goal' in cleaned_data:  # Alternative field name
        #     cleaned_data['impression_goal'] = cleaned_data.pop('impressions_goal')

        return cleaned_data

    @staticmethod
    def normalize_field_names(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize field names to match model expectations.

        This method converts various field name formats to the standard
        format expected by the Campaign model.

        Args:
            data: Dictionary with potentially non-standard field names

        Returns:
            Dict[str, Any]: Data with normalized field names

        Example:
            >>> cleaner = CampaignDataCleaner()
            >>> data = {"campaignName": "Test", "impressionGoal": 1000}
            >>> normalized = cleaner.normalize_field_names(data)
            >>> assert normalized["name"] == "Test"
            >>> assert normalized["impression_goal"] == 1000
        """
        cleaned_data = copy.deepcopy(data)

        # Field name normalization mappings
        field_mappings = {
            # camelCase -> snake_case
            'campaignName': 'name',
            'impressionGoal': 'impression_goal',
            'budgetEur': 'budget_eur',
            'cpmEur': 'cpm_eur',
            'runtimeStart': 'runtime_start',
            'runtimeEnd': 'runtime_end',
            'isRunning': 'is_running',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',

            # Alternative field names from different data sources
            'impressions_goal': 'impression_goal',
            'campaign_budget': 'budget_eur',
            'cost_per_mille': 'cpm_eur',
            'buyer_name': 'buyer',
        }

        # Apply field name mappings
        for old_name, new_name in field_mappings.items():
            if old_name in cleaned_data:
                cleaned_data[new_name] = cleaned_data.pop(old_name)

        return cleaned_data

    @staticmethod
    def clean_string_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean string fields by trimming whitespace and handling empty strings.

        Args:
            data: Dictionary with potentially unclean string fields

        Returns:
            Dict[str, Any]: Data with cleaned string fields

        Example:
            >>> cleaner = CampaignDataCleaner()
            >>> data = {"name": "  Test Campaign  ", "buyer": ""}
            >>> cleaned = cleaner.clean_string_fields(data)
            >>> assert cleaned["name"] == "Test Campaign"
            >>> assert cleaned["buyer"] == ""  # Empty string preserved
        """
        cleaned_data = copy.deepcopy(data)

        # String fields that should be trimmed
        string_fields = ['name', 'buyer', 'runtime', 'campaign_type']

        for field in string_fields:
            if field in cleaned_data and isinstance(cleaned_data[field], str):
                cleaned_data[field] = cleaned_data[field].strip()

        return cleaned_data

    @staticmethod
    def apply_all_cleaning(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all data cleaning operations in the correct order.

        This is a convenience method that applies all cleaning operations
        in the proper sequence to ensure data quality.

        Args:
            data: Raw campaign data dictionary

        Returns:
            Dict[str, Any]: Fully cleaned campaign data

        Example:
            >>> cleaner = CampaignDataCleaner()
            >>> raw_data = {"campaignName": "  Test  ", "cmp_eur": 2.5}
            >>> clean_data = cleaner.apply_all_cleaning(raw_data)
            >>> assert clean_data["name"] == "Test"
            >>> assert clean_data["cpm_eur"] == 2.5
        """
        # Apply cleaning operations in order
        cleaned_data = data

        # 1. Field corrections (handle known typos)
        cleaned_data = CampaignDataCleaner.apply_field_corrections(cleaned_data)

        # 2. Field name normalization (standardize field names)
        cleaned_data = CampaignDataCleaner.normalize_field_names(cleaned_data)

        # 3. String field cleaning (trim whitespace)
        cleaned_data = CampaignDataCleaner.clean_string_fields(cleaned_data)

        return cleaned_data


# =============================================================================
# DATA QUALITY ANALYSIS UTILITIES
# =============================================================================

class DataQualityAnalyzer:
    """
    Utilities for analyzing data quality issues in campaign data.

    This class helps identify common data quality problems that might
    need additional cleaning rules.
    """

    @staticmethod
    def analyze_field_variations(data_list: list) -> Dict[str, set]:
        """
        Analyze field name variations across multiple data records.

        This helps identify field name inconsistencies that might need
        normalization rules.

        Args:
            data_list: List of data dictionaries to analyze

        Returns:
            Dict[str, set]: Field names grouped by similarity

        Example:
            >>> analyzer = DataQualityAnalyzer()
            >>> data = [{"name": "A"}, {"campaignName": "B"}, {"campaign_name": "C"}]
            >>> variations = analyzer.analyze_field_variations(data)
            >>> print(variations)  # Shows name variations
        """
        field_variations = {}

        for data_dict in data_list:
            for field_name in data_dict.keys():
                # Group similar field names (simplified logic)
                base_name = field_name.lower().replace('_', '').replace(' ', '')

                if base_name not in field_variations:
                    field_variations[base_name] = set()

                field_variations[base_name].add(field_name)

        return field_variations

    @staticmethod
    def identify_empty_fields(data_dict: Dict[str, Any]) -> list:
        """
        Identify fields that are empty or contain only whitespace.

        Args:
            data_dict: Data dictionary to analyze

        Returns:
            list: List of field names that are empty

        Example:
            >>> analyzer = DataQualityAnalyzer()
            >>> data = {"name": "Test", "buyer": "", "notes": "   "}
            >>> empty_fields = analyzer.identify_empty_fields(data)
            >>> assert "buyer" in empty_fields
            >>> assert "notes" in empty_fields
        """
        empty_fields = []

        for field_name, value in data_dict.items():
            if value is None:
                empty_fields.append(field_name)
            elif isinstance(value, str) and not value.strip():
                empty_fields.append(field_name)

        return empty_fields


# =============================================================================
# USAGE EXAMPLES AND INTEGRATION GUIDE
# =============================================================================

"""
USAGE EXAMPLES:
==============

# In Campaign model constructor:
from app.validators.campaign_data_cleaner import CampaignDataCleaner

def __init__(self, **kwargs):
    # Clean data before validation
    cleaner = CampaignDataCleaner()
    cleaned_kwargs = cleaner.apply_all_cleaning(kwargs)

    # Continue with validation using cleaned data
    if 'id' in cleaned_kwargs:
        cleaned_kwargs['id'] = self.validate_uuid(cleaned_kwargs['id'])

    # ... rest of constructor logic

# In data import services:
from app.validators.campaign_data_cleaner import CampaignDataCleaner

def import_campaigns_from_xlsx(file_path):
    cleaner = CampaignDataCleaner()

    for row_data in parse_xlsx(file_path):
        # Clean each row before creating Campaign
        clean_data = cleaner.apply_all_cleaning(row_data)
        campaign = Campaign(**clean_data)
        # ... save campaign

INTEGRATION WITH CONSTRUCTOR REFACTORING:
========================================

The CampaignDataCleaner integrates with constructor refactoring as follows:

1. BEFORE validation: Clean the data
2. DURING validation: Use CampaignDataValidator for reusable validations
3. AFTER validation: Apply campaign-specific business rules

This separation provides:
✅ Clear separation of concerns (cleaning vs validation vs business rules)
✅ Reusable data cleaning logic across different entry points
✅ Better maintainability when data sources change
✅ Easier testing of data quality logic in isolation

DESIGN PRINCIPLES:
=================

1. ENCAPSULATE DATA QUALITY CONCERNS:
   - Keep data cleaning separate from business validation
   - Handle known data quality issues systematically
   - Provide utilities for identifying new quality issues

2. PRESERVE BACKWARD COMPATIBILITY:
   - Don't break existing data that's already clean
   - Apply corrections only when needed
   - Maintain existing field values when possible

3. SUPPORT MULTIPLE DATA SOURCES:
   - Handle field name variations from different sources
   - Normalize data to consistent format
   - Provide flexibility for future data sources

4. MAINTAIN AUDITABILITY:
   - Document what corrections are applied
   - Keep correction logic explicit and reviewable
   - Provide analysis tools for data quality assessment
"""