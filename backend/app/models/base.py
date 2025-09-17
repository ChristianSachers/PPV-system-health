"""
Base Model Classes for Campaign Data Foundation

This module provides:
1. Common base class for all database models
2. Timestamp tracking (created_at, updated_at)
3. Common model patterns and utilities
4. UUID validation helpers

Educational Focus: Shows how to create reusable base classes that provide
common functionality across all database models in the system.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from uuid import UUID
import uuid

# Import Base from database module to ensure single instance
from ..database import Base


class TimestampMixin:
    """
    Mixin class that adds timestamp fields to models.

    Provides automatic created_at and updated_at tracking.
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model class for all database models.

    Provides:
    - Automatic timestamp tracking
    - Common utility methods
    - Consistent model patterns
    """
    __abstract__ = True

    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary.

        Returns:
            dict: Dictionary representation of the model
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update_from_dict(self, data: dict) -> None:
        """
        Update model instance from dictionary.

        Args:
            data: Dictionary of field names and values to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """String representation of the model"""
        class_name = self.__class__.__name__
        primary_key = getattr(self, 'id', 'unknown')
        return f"<{class_name}(id={primary_key})>"


class UUIDValidationMixin:
    """
    Mixin class for models that use UUID primary keys.

    Provides UUID validation and utility methods.
    """

    @staticmethod
    def validate_uuid(uuid_string: str) -> str:
        """
        Validate UUID format and return normalized string.

        Args:
            uuid_string: String to validate as UUID

        Returns:
            str: Validated UUID string

        Raises:
            ValueError: If UUID format is invalid
        """
        if not uuid_string:
            raise ValueError("UUID cannot be empty")

        if not isinstance(uuid_string, str):
            raise ValueError("UUID must be a string")

        try:
            # Validate by parsing as UUID and converting back to string
            uuid_obj = UUID(uuid_string)
            return str(uuid_obj)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format: {uuid_string}") from e

    @staticmethod
    def generate_uuid() -> str:
        """
        Generate a new UUID string.

        Returns:
            str: New UUID string
        """
        return str(uuid.uuid4())


class CampaignBusinessRuleMixin:
    """
    Mixin class for campaign-specific business rules.

    Provides common validation and calculation methods.
    """

    def validate_positive_value(self, field_name: str, value: float) -> float:
        """
        Validate that a numeric value is positive.

        Args:
            field_name: Name of the field being validated
            value: Value to validate

        Returns:
            float: Validated value

        Raises:
            ValueError: If value is not positive
        """
        if value <= 0:
            raise ValueError(f"{field_name} must be positive, got: {value}")
        return value

    def validate_impression_goal_range(self, impression_goal: int) -> int:
        """
        Validate impression goal is within business constraints.

        Args:
            impression_goal: Impression goal value to validate

        Returns:
            int: Validated impression goal

        Raises:
            ValueError: If impression goal is outside valid range
        """
        MIN_IMPRESSION_GOAL = 1
        MAX_IMPRESSION_GOAL = 2_000_000_000

        if not isinstance(impression_goal, int):
            raise ValueError(f"Impression goal must be integer, got: {type(impression_goal)}")

        if impression_goal < MIN_IMPRESSION_GOAL:
            raise ValueError(f"Impression goal must be at least {MIN_IMPRESSION_GOAL}, got: {impression_goal}")

        if impression_goal > MAX_IMPRESSION_GOAL:
            raise ValueError(f"Impression goal cannot exceed {MAX_IMPRESSION_GOAL}, got: {impression_goal}")

        return impression_goal

    def validate_date_logic(self, start_date, end_date) -> None:
        """
        Validate date logic constraints.

        Args:
            start_date: Campaign start date (can be None for ASAP)
            end_date: Campaign end date (required)

        Raises:
            ValueError: If date logic is invalid
        """
        if end_date is None:
            raise ValueError("End date is required")

        if start_date is not None and start_date > end_date:
            raise ValueError(f"Start date ({start_date}) cannot be after end date ({end_date})")


# Import all models here to ensure they're registered with Base
# This is important for Alembic migrations to work properly
def import_all_models():
    """
    Import all model modules to ensure they're registered with Base.

    This function should be called before creating migrations or tables.
    """
    try:
        from . import campaign  # Import campaign models
        # Add other model imports here as they're created
    except ImportError:
        # Models may not exist yet during initial development
        pass