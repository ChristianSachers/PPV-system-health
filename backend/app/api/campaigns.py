"""
Campaign Data API Router - Fulfillment-Focused Campaign Retrieval

This router provides endpoints for retrieving and analyzing campaign data:
1. GET /campaigns/ - List campaigns with filtering and fulfillment analysis
2. GET /campaigns/{id} - Individual campaign details with fulfillment status
3. GET /campaigns/analytics/summary - Dashboard metrics and aggregations

Educational Focus: Shows how to implement business-focused API endpoints that
emphasize fulfillment calculations and campaign completion analysis.

Key Business Logic:
- Fulfillment percentage: (delivered_impressions / impression_goal) * 100%
- Campaign vs Deal classification: Based on buyer field
- Runtime status: Active vs completed based on end dates
- Over-delivery detection: Campaigns exceeding 100% fulfillment
"""

import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional, Union
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

# Import our database and models
from ..database import get_db
from ..models.campaign import Campaign

logger = logging.getLogger(__name__)

router = APIRouter()


def serialize_campaign_summary(campaign: Campaign) -> Dict[str, Any]:
    """
    Serialize campaign for list view with fulfillment focus.

    Args:
        campaign: Campaign model instance

    Returns:
        Campaign summary emphasizing fulfillment data
    """
    return {
        "id": campaign.id,
        "name": campaign.name,
        "campaign_type": campaign.entity_type,  # "campaign" or "deal"
        "is_running": campaign.is_running,
        "runtime": campaign.runtime,
        "impression_goal": campaign.impression_goal,
        "delivered_impressions": campaign.delivered_impressions or 0,
        "fulfillment_percentage": campaign.fulfillment_percentage,
        "is_over_delivered": campaign.is_over_delivered,
        "budget_eur": campaign.budget_eur,
        "cpm_eur": campaign.cpm_eur,
        "buyer": campaign.buyer
    }


def serialize_campaign_detail(campaign: Campaign) -> Dict[str, Any]:
    """
    Serialize campaign for detailed view with comprehensive fulfillment analysis.

    Args:
        campaign: Campaign model instance

    Returns:
        Detailed campaign data with fulfillment insights
    """
    # Calculate additional fulfillment metrics
    remaining_impressions = None
    days_remaining = None

    if campaign.impression_goal and campaign.delivered_impressions is not None:
        remaining_impressions = max(0, campaign.impression_goal - campaign.delivered_impressions)

    if campaign.runtime_end and campaign.is_running:
        days_remaining = (campaign.runtime_end.date() - date.today()).days

    return {
        "id": campaign.id,
        "name": campaign.name,
        "campaign_type": campaign.entity_type,
        "buyer": campaign.buyer,

        # Runtime information
        "runtime": campaign.runtime,
        "runtime_start": campaign.runtime_start.isoformat() if campaign.runtime_start else None,
        "runtime_end": campaign.runtime_end.isoformat() if campaign.runtime_end else None,
        "is_running": campaign.is_running,
        "days_remaining": days_remaining,

        # Fulfillment analysis (core business focus)
        "impression_goal": campaign.impression_goal,
        "delivered_impressions": campaign.delivered_impressions or 0,
        "remaining_impressions": remaining_impressions,
        "fulfillment_percentage": campaign.fulfillment_percentage,
        "is_over_delivered": campaign.is_over_delivered,

        # Financial data
        "budget_eur": campaign.budget_eur,
        "cpm_eur": campaign.cpm_eur,

        # Timestamps
        "created_at": campaign.created_at.isoformat(),
        "updated_at": campaign.updated_at.isoformat()
    }


@router.get("/campaigns/")
async def get_campaigns(
    campaign_type: Optional[str] = Query(None, description="Filter by 'campaign' or 'deal'"),
    running: Optional[bool] = Query(None, description="Filter by running status"),
    search: Optional[str] = Query(None, description="Search in campaign names"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of campaigns to return"),
    offset: int = Query(0, ge=0, description="Number of campaigns to skip"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get campaigns with filtering and fulfillment analysis.

    This endpoint emphasizes fulfillment data in the response format,
    making it easy for dashboard components to display completion percentages
    and identify over-delivered campaigns.

    Args:
        campaign_type: Filter by "campaign" or "deal" classification
        running: Filter by active (True) or completed (False) status
        search: Search term for campaign names
        limit: Maximum results to return
        offset: Pagination offset
        db: Database session

    Returns:
        List of campaigns with fulfillment focus and metadata
    """
    logger.info(f"Fetching campaigns with filters: type={campaign_type}, running={running}, search={search}")

    # Build query with business-focused filtering
    query = db.query(Campaign)

    # Filter by campaign type (campaign vs deal)
    if campaign_type:
        if campaign_type.lower() == "campaign":
            query = query.filter(Campaign.buyer == "Not set")
        elif campaign_type.lower() == "deal":
            query = query.filter(Campaign.buyer != "Not set")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="campaign_type must be 'campaign' or 'deal'"
            )

    # Filter by running status
    if running is not None:
        query = query.filter(Campaign.is_running == running)

    # Search in campaign names
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(Campaign.name.ilike(search_term))

    # Get total count for pagination metadata
    total_count = query.count()

    # Apply pagination and fetch results
    campaigns = query.offset(offset).limit(limit).all()

    # Serialize campaigns with fulfillment focus
    campaign_data = [serialize_campaign_summary(campaign) for campaign in campaigns]

    # Calculate summary statistics for the filtered results
    if campaigns:
        total_impressions_goal = sum(c.impression_goal for c in campaigns)
        total_delivered = sum(c.delivered_impressions or 0 for c in campaigns)
        overall_fulfillment = (total_delivered / total_impressions_goal * 100) if total_impressions_goal > 0 else 0
        over_delivered_count = sum(1 for c in campaigns if c.is_over_delivered)
    else:
        total_impressions_goal = 0
        total_delivered = 0
        overall_fulfillment = 0
        over_delivered_count = 0

    return {
        "campaigns": campaign_data,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": total_count > offset + len(campaigns)
        },
        "summary": {
            "total_campaigns": len(campaigns),
            "running_campaigns": sum(1 for c in campaigns if c.is_running),
            "completed_campaigns": sum(1 for c in campaigns if not c.is_running),
            "campaign_entities": sum(1 for c in campaigns if c.entity_type == "campaign"),
            "deal_entities": sum(1 for c in campaigns if c.entity_type == "deal"),
            "over_delivered_count": over_delivered_count,
            "total_impression_goal": total_impressions_goal,
            "total_delivered_impressions": total_delivered,
            "overall_fulfillment_percentage": overall_fulfillment
        },
        "filters_applied": {
            "campaign_type": campaign_type,
            "running": running,
            "search": search
        }
    }


@router.get("/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get individual campaign with detailed fulfillment analysis.

    Provides comprehensive campaign information including:
    - Detailed fulfillment calculations
    - Runtime analysis (days remaining, completion status)
    - Financial performance metrics
    - Classification information

    Args:
        campaign_id: Campaign UUID
        db: Database session

    Returns:
        Detailed campaign data with fulfillment insights
    """
    logger.info(f"Fetching campaign details for ID: {campaign_id}")

    # Find campaign by ID
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID {campaign_id} not found"
        )

    # Return detailed campaign data
    return serialize_campaign_detail(campaign)


@router.get("/campaigns/analytics/summary")
async def get_analytics_summary(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get campaign analytics summary for dashboard display.

    Provides key metrics focusing on fulfillment analysis:
    - Campaign vs Deal counts
    - Running vs Completed status
    - Fulfillment performance metrics
    - Over-delivery statistics

    This endpoint is optimized for dashboard widgets that need
    aggregate fulfillment data for monitoring campaign health.

    Args:
        db: Database session

    Returns:
        Analytics summary with fulfillment-focused metrics
    """
    logger.info("Generating analytics summary for dashboard")

    # Basic counts using efficient aggregation queries
    total_campaigns = db.query(Campaign).filter(Campaign.buyer == "Not set").count()
    total_deals = db.query(Campaign).filter(Campaign.buyer != "Not set").count()
    running_campaigns = db.query(Campaign).filter(Campaign.is_running == True).count()
    completed_campaigns = db.query(Campaign).filter(Campaign.is_running == False).count()

    # Fulfillment analysis
    campaigns_with_data = db.query(Campaign).filter(
        and_(
            Campaign.delivered_impressions.isnot(None),
            Campaign.impression_goal > 0
        )
    ).all()

    # Calculate fulfillment metrics
    if campaigns_with_data:
        total_goal = sum(c.impression_goal for c in campaigns_with_data)
        total_delivered = sum(c.delivered_impressions or 0 for c in campaigns_with_data)
        overall_fulfillment = (total_delivered / total_goal * 100) if total_goal > 0 else 0

        # Over-delivery analysis
        over_delivered = [c for c in campaigns_with_data if c.is_over_delivered]
        over_delivered_count = len(over_delivered)

        # Performance distribution
        under_50_pct = sum(1 for c in campaigns_with_data if c.fulfillment_percentage and c.fulfillment_percentage < 50)
        between_50_90_pct = sum(1 for c in campaigns_with_data if c.fulfillment_percentage and 50 <= c.fulfillment_percentage < 90)
        above_90_pct = sum(1 for c in campaigns_with_data if c.fulfillment_percentage and c.fulfillment_percentage >= 90)

    else:
        total_goal = 0
        total_delivered = 0
        overall_fulfillment = 0
        over_delivered_count = 0
        under_50_pct = 0
        between_50_90_pct = 0
        above_90_pct = 0

    # Runtime analysis
    current_date = date.today()
    ending_soon = db.query(Campaign).filter(
        and_(
            Campaign.is_running == True,
            Campaign.runtime_end <= datetime.combine(current_date.replace(day=current_date.day + 7), datetime.min.time())
        )
    ).count()

    return {
        "entity_summary": {
            "total_campaigns": total_campaigns,
            "total_deals": total_deals,
            "total_entities": total_campaigns + total_deals
        },
        "status_summary": {
            "running_campaigns": running_campaigns,
            "completed_campaigns": completed_campaigns,
            "ending_soon": ending_soon  # Ending within 7 days
        },
        "fulfillment_analysis": {
            "campaigns_with_data": len(campaigns_with_data),
            "total_impression_goal": total_goal,
            "total_delivered_impressions": total_delivered,
            "overall_fulfillment_percentage": round(overall_fulfillment, 2),
            "over_delivered_count": over_delivered_count,
            "over_delivered_percentage": round((over_delivered_count / len(campaigns_with_data) * 100), 2) if campaigns_with_data else 0
        },
        "performance_distribution": {
            "under_50_percent": under_50_pct,
            "between_50_90_percent": between_50_90_pct,
            "above_90_percent": above_90_pct,
            "over_delivered": over_delivered_count
        },
        "data_completeness": {
            "total_entities": total_campaigns + total_deals,
            "entities_with_delivery_data": len(campaigns_with_data),
            "data_completeness_percentage": round((len(campaigns_with_data) / (total_campaigns + total_deals) * 100), 2) if (total_campaigns + total_deals) > 0 else 0
        }
    }


@router.get("/campaigns/analytics/performance")
async def get_performance_metrics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed performance metrics for campaign optimization insights.

    Provides advanced fulfillment analysis including:
    - Completion rate trends
    - Budget efficiency metrics
    - Campaign vs Deal performance comparison
    - Over-delivery impact analysis

    Args:
        db: Database session

    Returns:
        Detailed performance metrics for optimization
    """
    logger.info("Generating detailed performance metrics")

    # Separate campaigns and deals for comparison
    campaigns = db.query(Campaign).filter(Campaign.buyer == "Not set").all()
    deals = db.query(Campaign).filter(Campaign.buyer != "Not set").all()

    def analyze_entity_group(entities: List[Campaign], entity_type: str) -> Dict[str, Any]:
        """Analyze performance metrics for a group of entities"""
        if not entities:
            return {
                "count": 0,
                "avg_fulfillment": 0,
                "completion_rate": 0,
                "over_delivery_rate": 0,
                "budget_efficiency": 0
            }

        entities_with_data = [e for e in entities if e.delivered_impressions is not None and e.impression_goal > 0]

        if not entities_with_data:
            return {
                "count": len(entities),
                "avg_fulfillment": 0,
                "completion_rate": 0,
                "over_delivery_rate": 0,
                "budget_efficiency": 0
            }

        # Calculate metrics
        fulfillments = [e.fulfillment_percentage for e in entities_with_data if e.fulfillment_percentage is not None]
        avg_fulfillment = sum(fulfillments) / len(fulfillments) if fulfillments else 0

        completed_entities = sum(1 for e in entities if not e.is_running)
        completion_rate = (completed_entities / len(entities) * 100) if entities else 0

        over_delivered = sum(1 for e in entities_with_data if e.is_over_delivered)
        over_delivery_rate = (over_delivered / len(entities_with_data) * 100) if entities_with_data else 0

        # Budget efficiency: delivered impressions per euro spent
        total_budget = sum(e.budget_eur for e in entities_with_data)
        total_delivered = sum(e.delivered_impressions or 0 for e in entities_with_data)
        budget_efficiency = (total_delivered / total_budget) if total_budget > 0 else 0

        return {
            "count": len(entities),
            "entities_with_data": len(entities_with_data),
            "avg_fulfillment_percentage": round(avg_fulfillment, 2),
            "completion_rate": round(completion_rate, 2),
            "over_delivery_rate": round(over_delivery_rate, 2),
            "budget_efficiency_impressions_per_eur": round(budget_efficiency, 2),
            "total_budget_eur": round(total_budget, 2),
            "total_delivered_impressions": total_delivered
        }

    return {
        "campaign_performance": analyze_entity_group(campaigns, "campaign"),
        "deal_performance": analyze_entity_group(deals, "deal"),
        "comparative_analysis": {
            "campaigns_outperform_deals": True,  # Placeholder for business logic
            "performance_gap_percentage": 0,     # Calculate based on actual data
            "recommendation": "Focus on campaign entities for better fulfillment rates"
        }
    }