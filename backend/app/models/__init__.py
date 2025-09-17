"""
Models package for Campaign Data Foundation

Imports all model classes for easy access and ensures they're registered
with SQLAlchemy Base for migrations and table creation.
"""

from .base import Base, BaseModel, UUIDValidationMixin, CampaignBusinessRuleMixin
from .campaign import Campaign, UploadSession

# Ensure all models are imported so they're registered with Base
__all__ = [
    'Base',
    'BaseModel',
    'UUIDValidationMixin',
    'CampaignBusinessRuleMixin',
    'Campaign',
    'UploadSession'
]