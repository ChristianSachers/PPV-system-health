"""
Campaign Model for Campaign Data Foundation

This model implements the corrected requirements:
1. impression_goal: INTEGER field (1 to 2,000,000,000) - NOT a range string
2. runtime: TEXT field ("ASAP-30.06.2025" or "07.07.2025-24.07.2025") - NOT separate fields
3. Application Focus: Fulfillment analysis = (delivered_impressions / impression_goal) * 100%
4. UUID preservation from XLSX data
5. Campaign vs Deal classification based on buyer field

Educational Focus: Shows how to implement business rules at the model level
while maintaining data integrity and supporting fulfillment analysis.
"""

from datetime import date, datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from typing import Optional

from .base import BaseModel, UUIDValidationMixin, CampaignBusinessRuleMixin


class Campaign(BaseModel, UUIDValidationMixin, CampaignBusinessRuleMixin):
    """
    Campaign model with corrected fulfillment-focused structure.

    Key Corrections Applied:
    - impression_goal: INTEGER field (was range string)
    - runtime: TEXT field preserving original format (was separate start/end fields)
    - Focus on fulfillment calculation: delivered / goal * 100%
    """
    __tablename__ = "campaigns"

    # Primary key - UUID from XLSX (preserved exactly)
    id = Column(String, primary_key=True)

    # Basic campaign information
    name = Column(String, nullable=False)

    # CORRECTED: Runtime as TEXT field preserving original format
    # Examples: "ASAP-30.06.2025", "07.07.2025-24.07.2025"
    runtime = Column(Text, nullable=False)

    # CORRECTED: Impression goal as single INTEGER value
    # Range: 1 to 2,000,000,000 (no longer a range string)
    impression_goal = Column(Integer, nullable=False)

    # Financial data (European format converted to float)
    budget_eur = Column(Float, nullable=False)
    cpm_eur = Column(Float, nullable=False)

    # Classification field for Campaign vs Deal determination
    buyer = Column(String, nullable=False)

    # Parsed runtime dates (computed from runtime TEXT field)
    runtime_start = Column(DateTime, nullable=True)  # None for ASAP campaigns
    runtime_end = Column(DateTime, nullable=False)

    # Campaign status (computed based on runtime_end vs current date)
    is_running = Column(Boolean, nullable=False, default=True)

    # Fulfillment tracking (will be populated by external data)
    delivered_impressions = Column(Integer, nullable=True, default=0)

    def __init__(self, **kwargs):
        """
        Initialize Campaign with business rule validation.

        Validates:
        - UUID format
        - Impression goal range
        - Positive financial values
        - Date logic constraints
        """
        # Extract and validate UUID
        if 'id' in kwargs:
            kwargs['id'] = self.validate_uuid(kwargs['id'])

        # Validate impression goal range
        if 'impression_goal' in kwargs:
            kwargs['impression_goal'] = self.validate_impression_goal_range(kwargs['impression_goal'])

        # Validate positive financial values
        if 'budget_eur' in kwargs:
            kwargs['budget_eur'] = self.validate_positive_value('Budget', kwargs['budget_eur'])

        if 'cmp_eur' in kwargs:
            kwargs['cpm_eur'] = self.validate_positive_value('CPM', kwargs['cpm_eur'])

        # Handle typo in test data (cmp_eur -> cpm_eur)
        if 'cmp_eur' in kwargs:
            kwargs['cpm_eur'] = kwargs.pop('cmp_eur')

        # Validate required fields
        if 'name' in kwargs and not kwargs['name'].strip():
            raise ValueError("Campaign name cannot be empty")

        if 'runtime' in kwargs:
            if not kwargs['runtime'].strip():
                raise ValueError("Runtime cannot be empty")
            # Parse runtime and set start/end dates
            self._parse_and_set_runtime_dates(kwargs)

        # Set buyer with proper handling
        if 'buyer' in kwargs and kwargs['buyer'] is None:
            raise ValueError("Buyer field is required")

        # Initialize parent
        super().__init__(**kwargs)

        # Calculate completion status after initialization
        if hasattr(self, 'runtime_end') and self.runtime_end:
            self.is_running = self._calculate_is_running()

    def _parse_and_set_runtime_dates(self, kwargs: dict) -> None:
        """
        Parse runtime TEXT field and set start/end date fields.

        Args:
            kwargs: Dictionary containing runtime field to parse
        """
        runtime_text = kwargs['runtime']

        try:
            if runtime_text.startswith('ASAP-'):
                # ASAP format: "ASAP-30.06.2025"
                end_date_str = runtime_text[5:]  # Remove "ASAP-"
                kwargs['runtime_start'] = None
                kwargs['runtime_end'] = self._parse_german_date(end_date_str)
            elif '-' in runtime_text and not runtime_text.startswith('ASAP'):
                # Standard format: "07.07.2025-24.07.2025"
                start_str, end_str = runtime_text.split('-', 1)
                kwargs['runtime_start'] = self._parse_german_date(start_str)
                kwargs['runtime_end'] = self._parse_german_date(end_str)
            else:
                raise ValueError(f"Invalid runtime format: {runtime_text}")

            # Validate date logic
            self.validate_date_logic(kwargs.get('runtime_start'), kwargs.get('runtime_end'))

        except Exception as e:
            raise ValueError(f"Error parsing runtime '{runtime_text}': {e}")

    def _parse_german_date(self, date_str: str) -> datetime:
        """
        Parse German date format (DD.MM.YYYY) to datetime.

        Args:
            date_str: Date string in German format

        Returns:
            datetime: Parsed date as datetime object
        """
        try:
            # Parse DD.MM.YYYY format
            day, month, year = date_str.strip().split('.')
            parsed_date = date(int(year), int(month), int(day))
            return datetime.combine(parsed_date, datetime.min.time())
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid German date format '{date_str}'. Expected DD.MM.YYYY") from e

    def _calculate_is_running(self) -> bool:
        """
        Calculate if campaign is currently running.

        Business Rule: Campaign is running if runtime_end > current_date

        Returns:
            bool: True if campaign is running, False if completed
        """
        if not self.runtime_end:
            return True  # Should not happen, but safe default

        current_date = date.today()
        campaign_end_date = self.runtime_end.date()

        return campaign_end_date > current_date

    @hybrid_property
    def entity_type(self) -> str:
        """
        Determine if this is a campaign or deal based on buyer field.

        Business Rule:
        - buyer = 'Not set' → campaign
        - buyer = anything else → deal

        Returns:
            str: 'campaign' or 'deal'
        """
        return 'campaign' if self.buyer == 'Not set' else 'deal'

    @hybrid_property
    def fulfillment_percentage(self) -> Optional[float]:
        """
        Calculate fulfillment percentage.

        Core Business Logic: (delivered_impressions / impression_goal) * 100%

        Returns:
            Optional[float]: Fulfillment percentage, None if no delivered data
        """
        if self.delivered_impressions is None or self.impression_goal is None:
            return None

        if self.impression_goal == 0:
            return None  # Avoid division by zero

        return (self.delivered_impressions / self.impression_goal) * 100.0

    @hybrid_property
    def is_over_delivered(self) -> bool:
        """
        Check if campaign is over-delivered (>100% fulfillment).

        Returns:
            bool: True if over-delivered, False otherwise
        """
        fulfilment = self.fulfillment_percentage
        return fulfilment is not None and fulfilment > 100.0

    @hybrid_property
    def campaign_type(self) -> str:
        """
        Legacy alias for entity_type.

        Returns:
            str: 'campaign' or 'deal'
        """
        return self.entity_type

    def update_delivered_impressions(self, delivered: int) -> None:
        """
        Update delivered impressions and recalculate fulfillment.

        Args:
            delivered: Number of delivered impressions
        """
        if delivered < 0:
            raise ValueError("Delivered impressions cannot be negative")

        self.delivered_impressions = delivered

    def get_fulfillment_status(self) -> dict:
        """
        Get comprehensive fulfillment status information.

        Returns:
            dict: Fulfillment status details
        """
        fulfillment_pct = self.fulfillment_percentage

        return {
            'campaign_id': self.id,
            'impression_goal': self.impression_goal,
            'delivered_impressions': self.delivered_impressions or 0,
            'fulfillment_percentage': fulfillment_pct,
            'is_over_delivered': self.is_over_delivered,
            'is_running': self.is_running,
            'entity_type': self.entity_type
        }

    def __repr__(self) -> str:
        """String representation focusing on fulfillment data"""
        fulfillment = self.fulfillment_percentage
        fulfillment_str = f"{fulfillment:.1f}%" if fulfillment is not None else "N/A"

        return (f"<Campaign(id={self.id[:8]}..., "
                f"name='{self.name[:30]}...', "
                f"type={self.entity_type}, "
                f"fulfillment={fulfillment_str})>")


class UploadSession(BaseModel):
    """
    Model to track XLSX upload sessions and processing status.

    Supports consecutive upload logic and validation reporting.
    """
    __tablename__ = "upload_sessions"

    id = Column(String, primary_key=True, default=lambda: UUIDValidationMixin.generate_uuid())

    # Upload metadata
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Processing status
    status = Column(String, nullable=False, default="processing")  # processing, completed, failed
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)

    # Results tracking
    total_rows_processed = Column(Integer, nullable=True)
    successful_campaigns = Column(Integer, nullable=True)
    failed_campaigns = Column(Integer, nullable=True)

    # Validation results (JSON stored as text)
    validation_errors = Column(Text, nullable=True)  # JSON string of errors
    processing_log = Column(Text, nullable=True)  # Detailed processing log

    def mark_processing_started(self) -> None:
        """Mark upload session as processing started"""
        self.status = "processing"
        self.processing_started_at = datetime.utcnow()

    def mark_completed(self, successful: int, failed: int, total: int) -> None:
        """Mark upload session as completed with results"""
        self.status = "completed"
        self.processing_completed_at = datetime.utcnow()
        self.successful_campaigns = successful
        self.failed_campaigns = failed
        self.total_rows_processed = total

    def mark_failed(self, error_message: str) -> None:
        """Mark upload session as failed"""
        self.status = "failed"
        self.processing_completed_at = datetime.utcnow()
        self.validation_errors = error_message