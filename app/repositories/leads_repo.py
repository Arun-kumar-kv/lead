#Step 4: Repository with Your Exact Queries
#python# app/repositories/leads_repo.py
"""
Repository for TERP_LEADS queries
Implements both live queries and snapshot queries
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case, text, and_
from typing import Dict, List, Any
from datetime import datetime, date, timedelta
from app.models.reflected_models import (
    TerpLeads, 
    TerpLeadsConversion,
    TerpLeadsChannel,
    TerpLeadsRatings,
    TerpLeadsStatus
)

class LeadsRepository:
    def __init__(self, db: Session):
        self.db = db

    # --------------------------------------------------
    # 1️⃣ Total Active Leads (Safe & Simple)
    # --------------------------------------------------
    def get_total_leads_live(self) -> int:
        """
        Live query: Total active leads
        """
        return (
            self.db.query(func.count(TerpLeads.ID))
            .filter(TerpLeads.ACTIVE == 1)
            .scalar()
            or 0
        )

    # --------------------------------------------------
    # 2️⃣ Dynamic Conversion Breakdown (NO HARDCODING)
    # --------------------------------------------------
    def get_conversion_breakdown_live(self) -> Dict[str, int]:
        """
        Live query: Conversion stage breakdown (dynamic)
        Automatically adapts if new conversion stages are added.
        """

        results = (
            self.db.query(
                TerpLeadsConversion.CONVERSION.label("conversion"),
                func.count(TerpLeads.ID).label("count"),
            )
            .outerjoin(
                TerpLeads,
                TerpLeads.CONVERSION_STATUS == TerpLeadsConversion.ID,
            )
            .filter(TerpLeads.ACTIVE == 1)
            .group_by(TerpLeadsConversion.CONVERSION)
            .all()
        )

        breakdown = {row.conversion: row.count for row in results if row.conversion}

        # Add total count separately (cleaner & accurate)
        breakdown["total_leads"] = self.get_total_leads_live()

        return breakdown

    # --------------------------------------------------
    # 3️⃣ Dynamic Ratings Breakdown (NO ID HARDCODING)
    # --------------------------------------------------
    def get_leads_by_ratings_live(self) -> List[Dict[str, Any]]:
        """
        Live query: Lead count grouped by rating (dynamic)
        Automatically includes new ratings.
        """

        results = (
            self.db.query(
                TerpLeadsRatings.RATINGS.label("rating"),
                func.count(TerpLeads.ID).label("lead_count"),
            )
            .outerjoin(
                TerpLeads,
                TerpLeads.LEADS_RATINGS == TerpLeadsRatings.ID,
            )
            .filter(TerpLeads.ACTIVE == 1)
            .group_by(TerpLeadsRatings.RATINGS)
            .order_by(func.count(TerpLeads.ID).desc())
            .all()
        )

        return [
            {
                "rating": row.rating,
                "lead_count": row.lead_count,
            }
            for row in results
            if row.rating
        ]

    # --------------------------------------------------
    # 4️⃣ Recent Leads (Already Good — Minor Cleanup)
    # --------------------------------------------------
    def get_recent_leads_live(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Live query: Recent lead inquiries with full joins
        """

        results = (
            self.db.query(
                TerpLeads.LEADS_CODE,
                TerpLeads.NAME,
                TerpLeads.INQUIRY_DATE,
                TerpLeads.LEADS_TYPE,
                TerpLeadsChannel.CHANNEL,
                TerpLeadsRatings.RATINGS,
                TerpLeadsStatus.STATUS,
                TerpLeadsConversion.CONVERSION.label("conversion_stage"),
                TerpLeads.PROPERTY_ID,
                TerpLeads.PROPERTY_UNIT,
                TerpLeads.CITY,
                TerpLeads.CREATED_BY,
                TerpLeads.LAST_UPDATED_AT,
            )
            .outerjoin(
                TerpLeadsChannel,
                TerpLeadsChannel.ID == TerpLeads.LEADS_CHANNEL,
            )
            .outerjoin(
                TerpLeadsRatings,
                TerpLeadsRatings.ID == TerpLeads.LEADS_RATINGS,
            )
            .outerjoin(
                TerpLeadsStatus,
                TerpLeadsStatus.ID == TerpLeads.LEADS_STATUS,
            )
            .outerjoin(
                TerpLeadsConversion,
                TerpLeadsConversion.ID == TerpLeads.CONVERSION_STATUS,
            )
            .filter(TerpLeads.ACTIVE == 1)
            .order_by(TerpLeads.INQUIRY_DATE.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "leads_code": row.LEADS_CODE,
                "name": row.NAME,
                "inquiry_date": row.INQUIRY_DATE.isoformat()
                if row.INQUIRY_DATE
                else None,
                "leads_type": row.LEADS_TYPE,
                "channel": row.CHANNEL,
                "rating": row.RATINGS,
                "status": row.STATUS,
                "conversion_stage": row.conversion_stage,
                "property_id": row.PROPERTY_ID,
                "property_unit": row.PROPERTY_UNIT,
                "city": row.CITY,
                "created_by": row.CREATED_BY,
                "last_updated_at": row.LAST_UPDATED_AT.isoformat()
                if row.LAST_UPDATED_AT
                else None,
            }
            for row in results
        ]

    # --------------------------------------------------
    # 5️⃣ Today's Leads (Optimized for Index Usage)
    # --------------------------------------------------
    def get_todays_new_leads_live(self) -> int:
        """
        Live query: Leads created today
        Avoids func.date() to allow index usage.
        """

        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        tomorrow_start = today_start.replace(day=today_start.day + 1)

        return (
            self.db.query(func.count(TerpLeads.ID))
            .filter(
                and_(
                    TerpLeads.INQUIRY_DATE >= today_start,
                    TerpLeads.INQUIRY_DATE < tomorrow_start,
                    TerpLeads.ACTIVE == 1,
                )
            )
            .scalar()
            or 0
        )