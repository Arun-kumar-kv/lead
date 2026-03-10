#Step 4: Repository with Your Exact Queries
#python# app/repositories/leads_repo.py
"""
Repository for TERP_LEADS queries
Implements both live queries and snapshot queries
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case, text, and_, distinct, literal_column
from typing import Dict, List, Any
from datetime import datetime, date, timedelta
from app.models.reflected_models import (
    TerpLeads, 
    TerpLeadsConversion,
    TerpLeadsChannel,
    TerpLeadsRatings,
    TerpLeadsStatus,
    TerpLsLeadsEnquiry,
    TerpLsPropertyUnit,
    TerpLsPropertyUnitStatus,
    TerpLsProperty,
)

class LeadsRepository:
    def __init__(self, db: Session):
        self.db = db
    def _apply_filters(self, query, filters: dict):
        """Apply optional filters to any TerpLeads query."""
        if not filters:
            return query
        if filters.get("property_id"):
            query = query.filter(TerpLeads.PROPERTY_ID == filters["property_id"])
        if filters.get("property_type"):
            query = query.filter(TerpLeads.LEADS_TYPE == filters["property_type"])
        if filters.get("date_from"):
            date_from = datetime.strptime(filters["date_from"], "%Y-%m-%d")
            query = query.filter(TerpLeads.INQUIRY_DATE >= date_from)
        if filters.get("date_to"):
            date_to = datetime.strptime(filters["date_to"], "%Y-%m-%d")
            date_to = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(TerpLeads.INQUIRY_DATE <= date_to)
        return query
    # --------------------------------------------------
    # 1️⃣ Total Active Leads (Safe & Simple)
    # --------------------------------------------------
    def get_total_leads_live(self,filters: dict = None) -> int:
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
    def get_conversion_breakdown_live(self,filters: dict = None) -> Dict[str, int]:
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
    def get_leads_by_ratings_live(self,filters: dict = None) -> List[Dict[str, Any]]:
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
    def get_recent_leads_live(self, limit: int = 10,filters: dict = None) -> List[Dict[str, Any]]:
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
    def get_todays_new_leads_live(self,filters: dict = None) -> int:
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
    # --------------------------------------------------
    # 6️⃣ Lead → Enquiry Conversion Rate
    # --------------------------------------------------
    def get_lead_to_enquiry_conversion(self,filters: dict = None) -> Dict[str, Any]:
        """
        Live query: How many active leads converted to an enquiry,
        and what percentage that represents.
        """
        result = (
            self.db.query(
                func.count(distinct(TerpLeads.ID)).label("total_leads"),
                func.count(distinct(TerpLsLeadsEnquiry.LEAD_ID)).label("converted_to_enquiry"),
            )
            .outerjoin(TerpLsLeadsEnquiry, TerpLsLeadsEnquiry.LEAD_ID == TerpLeads.ID)
            .filter(TerpLeads.ACTIVE == 1)
            .one()
        )

        total = result.total_leads or 0
        converted = result.converted_to_enquiry or 0
        conversion_rate = round(converted * 100.0 / total, 2) if total else 0.0

        return {
            "total_leads": total,
            "converted_to_enquiry": converted,
            "conversion_rate_pct": conversion_rate,
        }

    # --------------------------------------------------
    # 7️⃣ Full Funnel Conversion Rates
    #    Lead → Enquiry → Tenant  (+ overall Lead → Tenant)
    # --------------------------------------------------
    def get_full_funnel_conversion(self,filters: dict = None) -> Dict[str, Any]:
        """
        Live query: Full conversion funnel rates.
        - Lead to Enquiry %
        - Enquiry to Tenant %
        - Lead to Tenant (overall) %

        NOTE: CONVERSION_STATUS = 4 is the 'Convert to Tenant' stage.
              Update the value if your lookup table differs.
        """
        TENANT_CONVERSION_ID = 4

        result = (
            self.db.query(
                func.count(distinct(TerpLeads.ID)).label("total_leads"),
                func.count(distinct(TerpLsLeadsEnquiry.LEAD_ID)).label("converted_to_enquiry"),
                func.count(
                    distinct(
                        case(
                            (TerpLeads.CONVERSION_STATUS == TENANT_CONVERSION_ID, TerpLeads.ID),
                            else_=None,
                        )
                    )
                ).label("converted_to_tenant"),
            )
            .outerjoin(TerpLsLeadsEnquiry, TerpLsLeadsEnquiry.LEAD_ID == TerpLeads.ID)
            .filter(TerpLeads.ACTIVE == 1)
            .one()
        )

        total_leads = result.total_leads or 0
        to_enquiry = result.converted_to_enquiry or 0
        to_tenant = result.converted_to_tenant or 0

        return {
            "total_leads": total_leads,
            "converted_to_enquiry": to_enquiry,
            "converted_to_tenant": to_tenant,
            "lead_to_enquiry_pct": round(to_enquiry * 100.0 / total_leads, 2) if total_leads else 0.0,
            "enquiry_to_tenant_pct": round(to_tenant * 100.0 / to_enquiry, 2) if to_enquiry else 0.0,
            "lead_to_tenant_conversion_pct": round(to_tenant * 100.0 / total_leads, 2) if total_leads else 0.0,
        }

    # --------------------------------------------------
    # 8️⃣ Vacant Units — Lead Coverage (Last 30 Days)
    # --------------------------------------------------
    def get_vacant_units_lead_coverage(self,filters: dict = None) -> Dict[str, Any]:
        """
        Live query: How well vacant units are covered by recent leads.
        Looks at leads created in the last 30 days.
        Returns counts, coverage %, avg leads per unit, and a sufficiency verdict.
        """
        cutoff = datetime.utcnow() - timedelta(days=30)

        result = (
            self.db.query(
                func.count(distinct(TerpLsPropertyUnit.ID)).label("total_vacant_units"),
                func.count(distinct(TerpLeads.PROPERTY_UNIT)).label("vacant_units_with_leads"),
                func.count(TerpLeads.ID).label("total_leads_on_vacant"),
            )
            .join(TerpLsPropertyUnitStatus, TerpLsPropertyUnit.STATUS == TerpLsPropertyUnitStatus.ID)
            .join(TerpLsProperty, TerpLsPropertyUnit.PROPERTY_ID == TerpLsProperty.ID)
            .outerjoin(
                TerpLeads,
                and_(
                    TerpLeads.PROPERTY_UNIT == TerpLsPropertyUnit.ID,
                    TerpLeads.CREATED_AT >= cutoff,
                ),
            )
            .filter(TerpLsPropertyUnitStatus.STATUS == "Available")
            .one()
        )

        total_vacant = result.total_vacant_units or 0
        units_with_leads = result.vacant_units_with_leads or 0
        total_leads = result.total_leads_on_vacant or 0

        avg_leads = round(total_leads / total_vacant, 2) if total_vacant else 0.0
        pct_covered = round(units_with_leads * 100.0 / total_vacant, 1) if total_vacant else 0.0

        if avg_leads == 0:
            verdict = "No Leads at All"
        elif avg_leads < 1:
            verdict = "Insufficient"
        elif avg_leads <= 2:
            verdict = "Sufficient"
        else:
            verdict = "Well Covered"

        return {
            "total_vacant_units": total_vacant,
            "vacant_units_with_leads": units_with_leads,
            "vacant_units_with_no_leads": total_vacant - units_with_leads,
            "pct_units_covered": pct_covered,
            "total_leads_on_vacant": total_leads,
            "avg_leads_per_vacant_unit": avg_leads,
            "sufficiency_verdict": verdict,
        }

    # --------------------------------------------------
    # 9️⃣ Vacant Units — High Leads but Low Conversion
    # --------------------------------------------------
    def get_vacant_units_high_leads_low_conversion(self,filters: dict = None) -> List[Dict[str, Any]]:
        """
        Live query: Vacant units that attract hot leads (LEADS_RATINGS = 7)
        but have a low conversion rate to tenant.
        Flags units with < 20% conversion as 'Low Conversion'.

        NOTE: LEADS_RATINGS = 7 represents 'Hot' leads in your lookup table.
              Update if your rating IDs differ.
        """
        HOT_RATING_ID = 7

        converted_to_tenant = func.sum(
            case(
                (TerpLeadsConversion.CONVERSION == "Convert to Tenant", 1),
                else_=0,
            )
        ).label("conversions")

        total_hot_leads = func.count(TerpLeads.ID).label("total_hot_leads")

        conversion_rate_expr = func.round(
            func.sum(
                case(
                    (TerpLeadsConversion.CONVERSION == "Convert to Tenant", 1),
                    else_=0,
                )
            )
            * 100.0
            / func.nullif(func.count(TerpLeads.ID), 0),
            1,
        ).label("conversion_rate_pct")

        results = (
            self.db.query(
                TerpLsProperty.NAME.label("property_name"),
                TerpLsPropertyUnit.CODE.label("unit_code"),
                TerpLsPropertyUnit.DESCRIPTION.label("unit_description"),
                total_hot_leads,
                converted_to_tenant,
                conversion_rate_expr,
            )
            .join(TerpLsPropertyUnitStatus, TerpLsPropertyUnit.STATUS == TerpLsPropertyUnitStatus.ID)
            .join(TerpLsProperty, TerpLsPropertyUnit.PROPERTY_ID == TerpLsProperty.ID)
            .join(TerpLeads, TerpLeads.PROPERTY_UNIT == TerpLsPropertyUnit.ID)
            .join(TerpLeadsConversion, TerpLeads.CONVERSION_STATUS == TerpLeadsConversion.ID)
            .filter(
                TerpLsPropertyUnitStatus.STATUS == "Available",
                TerpLeads.ACTIVE == 1,
                TerpLeads.LEADS_RATINGS == HOT_RATING_ID,
            )
            .group_by(
                TerpLsPropertyUnit.ID,
                TerpLsPropertyUnit.CODE,
                TerpLsPropertyUnit.DESCRIPTION,
                TerpLsProperty.NAME,
            )
            .having(func.count(TerpLeads.ID) > 0)
            .order_by(conversion_rate_expr.asc(), total_hot_leads.desc())
            .all()
        )

        return [
            {
                "property_name": row.property_name,
                "unit_code": row.unit_code,
                "unit_description": row.unit_description,
                "total_hot_leads": row.total_hot_leads,
                "conversions": row.conversions,
                "conversion_rate_pct": float(row.conversion_rate_pct) if row.conversion_rate_pct is not None else 0.0,
                "conversion_flag": (
                    "Low Conversion"
                    if (row.conversion_rate_pct or 0) < 20
                    else "Converting Well"
                ),
            }
            for row in results
        ]
