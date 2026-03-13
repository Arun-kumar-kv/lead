
"""
Repository for eq_ls_leads queries
Implements both live queries and snapshot queries
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case, text, and_, distinct, literal_column
from typing import Dict, List, Any
from datetime import datetime, date, timedelta
from sqlalchemy import Date, Interval
from sqlalchemy.sql.expression import cast
from dateutil.relativedelta import relativedelta  
from app.models.reflected_models import (
    EqLsLeads,
    EqLsLeadsConversion,
    EqLsLeadsChannel,
    EqLsLeadsRatings,
    EqLsLeadsStatus,
    EqLsLeadsEnquiry,
    EqLsLeadsEnquiryProp,
    EqLsLeadsEnquiryPropUnit,
    EqLsPropertyUnit,
    EqLsPropertyUnitStatus,
    EqLsProperty,
    EqLsTenantType
)


class LeadsRepository:
    def __init__(self, db: Session):
        self.db = db

    def _apply_filters(self, query, filters: dict):
        """Apply optional filters to any EqLsLeads query."""
        if not filters:
            return query
        if filters.get("property_id"):
            query = query.filter(EqLsLeads.PROPERTY_ID == filters["property_id"])
        if filters.get("property_type"):
            query = query.filter(EqLsLeads.LEADS_TYPE == filters["property_type"])
        if filters.get("date_from"):
            date_from = datetime.strptime(filters["date_from"], "%Y-%m-%d")
            query = query.filter(EqLsLeads.INQUIRY_DATE >= date_from)
        if filters.get("date_to"):
            date_to = datetime.strptime(filters["date_to"], "%Y-%m-%d")
            date_to = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(EqLsLeads.INQUIRY_DATE <= date_to)
        return query

    # 1️⃣ Total Leads
    def get_total_leads_live(self, filters: dict = None) -> int:
        query = (
            self.db.query(func.count(EqLsLeads.ID))
            .filter(EqLsLeads.status == True)
        )
        query = self._apply_filters(query, filters or {})
        return query.scalar() or 0

    # 2️⃣ Dynamic Conversion Breakdown
    def get_conversion_breakdown_live(self, filters: dict = None) -> Dict[str, int]:
        query = (
            self.db.query(
                EqLsLeadsConversion.CONVERSION.label("conversion"),
                func.count(EqLsLeads.ID).label("count"),
            )
            .outerjoin(
                EqLsLeads,
                EqLsLeads.CONVERSION_STATUS == EqLsLeadsConversion.ID,
            )
            .filter(EqLsLeads.status == True)
            .group_by(EqLsLeadsConversion.CONVERSION)
        )
        query = self._apply_filters(query, filters or {})
        results = query.all()

        breakdown = {row.conversion: row.count for row in results if row.conversion}
        breakdown["total_leads"] = self.get_total_leads_live(filters)
        return breakdown

    # 3️⃣ Dynamic Ratings Breakdown
    def get_leads_by_ratings_live(self, filters: dict = None) -> List[Dict[str, Any]]:
        query = (
            self.db.query(
                EqLsLeadsRatings.RATINGS.label("rating"),
                func.count(EqLsLeadsEnquiry.ID).label("lead_count"),
            )
            .outerjoin(
                EqLsLeadsEnquiry,
                EqLsLeadsEnquiry.enquiry_rating == EqLsLeadsRatings.ID,
            )
            .group_by(EqLsLeadsRatings.ID, EqLsLeadsRatings.RATINGS)
        )
        results = query.order_by(func.count(EqLsLeadsEnquiry.ID).desc()).all()

        return [
            {"rating": row.rating, "lead_count": row.lead_count}
            for row in results
            if row.lead_count > 0
        ]
    # def get_leads_by_ratings_live(self, filters: dict = None) -> List[Dict[str, Any]]:
    #     query = (
    #         self.db.query(
    #             EqLsLeadsRatings.RATINGS.label("rating"),
    #             func.count(EqLsLeads.ID).label("lead_count"),
    #         )
    #         .outerjoin(
    #             EqLsLeads,
    #             EqLsLeads.LEADS_RATINGS == EqLsLeadsRatings.ID,
    #         )
    #         .filter(EqLsLeads.status == True)
    #         .group_by(EqLsLeadsRatings.RATINGS)
    #     )
    #     query = self._apply_filters(query, filters or {})
    #     results = query.order_by(func.count(EqLsLeads.ID).desc()).all()

    #     return [
    #         {"rating": row.rating, "lead_count": row.lead_count}
    #         for row in results
    #         if row.rating
    #     ]

    # 4️⃣ Recent Leads
    def get_recent_leads_live(self, limit: int = 10, filters: dict = None) -> List[Dict[str, Any]]:
        query = (
            self.db.query(
                EqLsLeads.LEADS_CODE,
                EqLsLeads.NAME,
                EqLsLeads.INQUIRY_DATE,
                EqLsLeads.LEADS_TYPE,
                EqLsLeadsChannel.CHANNEL,
                EqLsLeadsRatings.RATINGS,
                EqLsLeadsStatus.STATUS,
                EqLsLeadsConversion.CONVERSION.label("conversion_stage"),
                EqLsLeads.PROPERTY_ID,
                EqLsLeads.UNIT_ID,
                EqLsLeads.CITY,
                EqLsLeads.CREATED_BY,
                EqLsLeads.LAST_UPDATED_AT,
            )
            .outerjoin(EqLsLeadsChannel, EqLsLeadsChannel.ID == EqLsLeads.LEADS_CHANNEL)
            .outerjoin(EqLsLeadsRatings, EqLsLeadsRatings.ID == EqLsLeads.LEADS_RATINGS)
            .outerjoin(EqLsLeadsStatus, EqLsLeadsStatus.ID == EqLsLeads.LEADS_STATUS)
            .outerjoin(EqLsLeadsConversion, EqLsLeadsConversion.ID == EqLsLeads.CONVERSION_STATUS)
            .filter(EqLsLeads.status == True)
        )
        query = self._apply_filters(query, filters or {})
        results = query.order_by(EqLsLeads.INQUIRY_DATE.desc()).limit(limit).all()

        return [
            {
                "leads_code": row.LEADS_CODE,
                "name": row.NAME,
                "inquiry_date": row.INQUIRY_DATE.isoformat() if row.INQUIRY_DATE else None,
                "leads_type": row.LEADS_TYPE,
                "channel": row.CHANNEL,
                "rating": row.RATINGS,
                "status": row.STATUS,
                "conversion_stage": row.conversion_stage,
                "property_id": row.PROPERTY_ID,
                "property_unit": row.UNIT_ID,
                "city": row.CITY,
                "created_by": row.CREATED_BY,
                "last_updated_at": row.LAST_UPDATED_AT.isoformat() if row.LAST_UPDATED_AT else None,
            }
            for row in results
        ]

    # 5️⃣ Today's Leads
    def get_todays_new_leads_live(self, filters: dict = None) -> int:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)

        query = (
            self.db.query(func.count(EqLsLeads.ID))
            .filter(
                and_(
                    EqLsLeads.INQUIRY_DATE >= today_start,
                    EqLsLeads.INQUIRY_DATE < tomorrow_start,
                    EqLsLeads.status == True,
                )
            )
        )
        query = self._apply_filters(query, filters or {})
        return query.scalar() or 0

    # 6️⃣ Lead → Enquiry Conversion Rate
    def get_lead_to_enquiry_conversion(self, filters: dict = None) -> Dict[str, Any]:
        query = (
            self.db.query(
                func.count(distinct(EqLsLeads.ID)).label("total_leads"),
                func.count(distinct(EqLsLeadsEnquiry.LEAD_ID)).label("converted_to_enquiry"),
            )
            .outerjoin(EqLsLeadsEnquiry, EqLsLeadsEnquiry.LEAD_ID == EqLsLeads.ID)
            .filter(EqLsLeads.status == True)
        )
        query = self._apply_filters(query, filters or {})
        result = query.one()

        total = result.total_leads or 0
        converted = result.converted_to_enquiry or 0
        return {
            "total_leads": total,
            "converted_to_enquiry": converted,
            "conversion_rate_pct": round(converted * 100.0 / total, 2) if total else 0.0,
        }

    # 7️⃣ Full Funnel Conversion Rates
    def get_full_funnel_conversion(self, filters: dict = None) -> Dict[str, Any]:
        TENANT_CONVERSION_ID = 4

        query = (
            self.db.query(
                func.count(distinct(EqLsLeads.ID)).label("total_leads"),
                func.count(distinct(EqLsLeadsEnquiry.LEAD_ID)).label("converted_to_enquiry"),
                func.count(
                    distinct(
                        case(
                            (EqLsLeads.CONVERSION_STATUS == TENANT_CONVERSION_ID, EqLsLeads.ID),
                            else_=None,
                        )
                    )
                ).label("converted_to_tenant"),
            )
            .outerjoin(EqLsLeadsEnquiry, EqLsLeadsEnquiry.LEAD_ID == EqLsLeads.ID)
            .filter(EqLsLeads.status == True)
        )
        query = self._apply_filters(query, filters or {})
        result = query.one()

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

    # 8️⃣ Vacant Units — Lead Coverage (Last 30 Days)
    def get_vacant_units_lead_coverage(self, filters: dict = None) -> Dict[str, Any]:
        query = (
            self.db.query(
                func.count(distinct(EqLsPropertyUnit.ID)).label("total_vacant_units"),
                func.count(distinct(EqLsLeadsEnquiry.UNIT_ID)).label("vacant_units_with_leads"),
            )
            .join(
                EqLsPropertyUnitStatus,
                EqLsPropertyUnit.STATUS == EqLsPropertyUnitStatus.ID
            )
            .outerjoin(
                EqLsLeadsEnquiry,
                EqLsLeadsEnquiry.UNIT_ID == EqLsPropertyUnit.ID
            )
            .filter(EqLsPropertyUnitStatus.STATUS == "Available")
        )
        result = query.one()

        total_vacant     = result.total_vacant_units or 0
        units_with_leads = result.vacant_units_with_leads or 0
        pct_covered      = round(units_with_leads * 100.0 / total_vacant, 2) if total_vacant else 0.0

        if pct_covered == 0:
            verdict = "No Leads at All"
        elif pct_covered < 50:
            verdict = "Insufficient"
        elif pct_covered <= 80:
            verdict = "Sufficient"
        else:
            verdict = "Well Covered"

        return {
            "total_vacant_units":        total_vacant,
            "vacant_units_with_leads":   units_with_leads,
            "vacant_units_with_no_leads": total_vacant - units_with_leads,
            "pct_units_covered":         pct_covered,
            "sufficiency_verdict":       verdict,
        }

    # 9️⃣ Vacant Units — High Leads but Low Conversion
    def get_vacant_units_high_leads_low_conversion(self, filters: dict = None) -> List[Dict[str, Any]]:
        HOT_RATING_ID = 7

        converted_to_tenant = func.sum(
            case((EqLsLeadsConversion.CONVERSION == "Convert to Tenant", 1), else_=0)
        ).label("conversions")

        total_hot_leads = func.count(EqLsLeads.ID).label("total_hot_leads")

        conversion_rate_expr = func.round(
            func.sum(
                case((EqLsLeadsConversion.CONVERSION == "Convert to Tenant", 1), else_=0)
            )
            * 100.0
            / func.nullif(func.count(EqLsLeads.ID), 0),
            1,
        ).label("conversion_rate_pct")

        query = (
            self.db.query(
                EqLsProperty.NAME.label("property_name"),
                EqLsPropertyUnit.CODE.label("unit_code"),
                EqLsPropertyUnit.DESCRIPTION.label("unit_description"),
                total_hot_leads,
                converted_to_tenant,
                conversion_rate_expr,
            )
            .join(EqLsPropertyUnitStatus, EqLsPropertyUnit.STATUS == EqLsPropertyUnitStatus.ID)
            .join(EqLsProperty, EqLsPropertyUnit.PROPERTY_ID == EqLsProperty.ID)
            .join(EqLsLeads, EqLsLeads.UNIT_ID == EqLsPropertyUnit.ID)
            .join(EqLsLeadsConversion, EqLsLeads.CONVERSION_STATUS == EqLsLeadsConversion.ID)
            .filter(
                EqLsPropertyUnitStatus.STATUS == "Available",
                EqLsLeads.status == True,
                EqLsLeads.LEADS_RATINGS == HOT_RATING_ID,
            )
        )
        query = self._apply_filters(query, filters or {})
        results = (
            query
            .group_by(EqLsPropertyUnit.ID, EqLsPropertyUnit.CODE, EqLsPropertyUnit.DESCRIPTION, EqLsProperty.NAME)
            .having(func.count(EqLsLeads.ID) > 0)
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
                "conversion_flag": "Low Conversion" if (row.conversion_rate_pct or 0) < 20 else "Converting Well",
            }
            for row in results
        ]

    # 🔟 Active vs Non-Active Leads Count
    def get_active_inactive_leads_count(self, filters: dict = None) -> Dict[str, Any]:
        query = (
            self.db.query(
                func.sum(case((EqLsLeads.status == True, 1), else_=0)).label("active_leads"),
                func.sum(case((EqLsLeads.status == False, 1), else_=0)).label("inactive_leads"),
                func.count(EqLsLeads.ID).label("total"),
            )
        )
        query = self._apply_filters(query, filters or {})
        result = query.one()
        active   = result.active_leads or 0
        inactive = result.inactive_leads or 0
        total    = result.total or 0
        return {
            "active_leads":   active,
            "inactive_leads": inactive,
            "total":          total,
            "active_pct":     round(float(active) * 100.0 / float(total), 2) if total else 0.0,
            "inactive_pct":   round(float(inactive) * 100.0 / float(total), 2) if total else 0.0,
        }

    # 1️⃣1️⃣ New Leads — Today / This Week / This Month
    def get_new_leads_periods(self, filters: dict = None) -> Dict[str, int]:
        now            = datetime.utcnow()
        today_start    = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)

        week_start  = today_start - timedelta(days=now.weekday())
        week_end    = week_start + timedelta(days=7)

        month_start = today_start.replace(day=1)
        if now.month == 12:
            month_end = today_start.replace(year=now.year + 1, month=1, day=1)
        else:
            month_end = today_start.replace(month=now.month + 1, day=1)

        query = (
            self.db.query(
                func.sum(
                    case((
                        and_(
                            EqLsLeads.INQUIRY_DATE >= today_start,
                            EqLsLeads.INQUIRY_DATE <  tomorrow_start,
                        ), 1), else_=0)
                ).label("leads_today"),
                func.sum(
                    case((
                        and_(
                            EqLsLeads.INQUIRY_DATE >= week_start,
                            EqLsLeads.INQUIRY_DATE <  week_end,
                        ), 1), else_=0)
                ).label("leads_this_week"),
                func.sum(
                    case((
                        and_(
                            EqLsLeads.INQUIRY_DATE >= month_start,
                            EqLsLeads.INQUIRY_DATE <  month_end,
                        ), 1), else_=0)
                ).label("leads_this_month"),
            )
            .filter(EqLsLeads.status == True)
        )
        query  = self._apply_filters(query, filters or {})
        result = query.one()
        return {
            "leads_today":      int(result.leads_today      or 0),
            "leads_this_week":  int(result.leads_this_week  or 0),
            "leads_this_month": int(result.leads_this_month or 0),
        }

    # 1️⃣2️⃣ Leads by Channel
    def get_leads_by_channel(self, filters: dict = None) -> List[Dict[str, Any]]:
        query = (
            self.db.query(
                EqLsLeadsChannel.CHANNEL.label("channel"),
                func.count(EqLsLeadsEnquiry.ID).label("count"),
            )
            .outerjoin(EqLsLeadsEnquiry, EqLsLeadsEnquiry.enquiry_channel == EqLsLeadsChannel.ID)
        )
        results = (
            query
            .group_by(EqLsLeadsChannel.ID, EqLsLeadsChannel.CHANNEL)
            .order_by(func.count(EqLsLeadsEnquiry.ID).desc())
            .all()
        )
        total = sum(row.count for row in results)
        return [
            {
                "channel":    row.channel,
                "count":      row.count,
                "percentage": round(row.count * 100.0 / total, 2) if total else 0.0,
            }
            for row in results
            if row.count > 0  # skip channels with zero enquiries
        ]
        
    # def get_leads_by_channel(self, filters: dict = None) -> List[Dict[str, Any]]:
    #     query = (
    #         self.db.query(
    #             EqLsLeadsChannel.CHANNEL.label("channel"),
    #             func.count(EqLsLeads.ID).label("count"),
    #         )
    #         .join(EqLsLeads, EqLsLeads.LEADS_CHANNEL == EqLsLeadsChannel.ID)
    #         .filter(EqLsLeads.status == True)
    #     )
    #     query = self._apply_filters(query, filters or {})
    #     results = (
    #         query
    #         .group_by(EqLsLeadsChannel.CHANNEL)
    #         .order_by(func.count(EqLsLeads.ID).desc())
    #         .all()
    #     )
    #     total = sum(row.count for row in results)
    #     return [
    #         {
    #             "channel":     row.channel,
    #             "count":       row.count,
    #             "percentage":  round(row.count * 100.0 / total, 2) if total else 0.0,
    #         }
    #         for row in results
    #     ]
    # 1️⃣3️⃣ Leads by Type (Individual vs Company)
    def get_leads_by_type(self, filters: dict = None) -> List[Dict[str, Any]]:
        results = (
            self.db.query(
                EqLsTenantType.NAME.label("type"),
                func.count(EqLsLeads.ID).label("count"),
            )
            .outerjoin(
                EqLsLeads,
                EqLsLeads.LEADS_TYPE == EqLsTenantType.ID,
            )
            .filter(EqLsLeads.status == True)
            .group_by(EqLsTenantType.ID, EqLsTenantType.NAME)
            .order_by(func.count(EqLsLeads.ID).desc())
            .all()
        )

        total = sum(row.count for row in results if row.count)
        return [
            {
                "type":       row.type,
                "count":      row.count or 0,
                "percentage": round((row.count or 0) * 100.0 / total, 1) if total else 0.0,
            }
            for row in results
            if (row.count or 0) > 0
        ]
    # 1️⃣4️⃣ Leads by Category (Inbound vs Outbound)

    def get_leads_by_category(self, filters: dict = None) -> List[Dict[str, Any]]:
        CATEGORY_MAP = {1: "Inbound", 2: "Outbound"}

        results = (
            self.db.query(
                EqLsLeads.lead_category.label("category_id"),
                func.count(EqLsLeads.ID).label("count"),
            )
            .filter(
                EqLsLeads.status == True,
                EqLsLeads.lead_category.isnot(None),
            )
            .group_by(EqLsLeads.lead_category)
            .order_by(EqLsLeads.lead_category)
            .all()
        )

        total = sum(row.count for row in results)
        return [
            {
                "category_id": int(row.category_id),                                        # ← cast to int
                "category":    CATEGORY_MAP.get(int(row.category_id), f"Category {row.category_id}"),  # ← cast to int
                "count":       row.count,
                "percentage":  round(row.count * 100.0 / total, 1) if total else 0.0,
            }
            for row in results
        ]
    # 1️⃣5️⃣ VIP Leads Stats
    def get_vip_leads_stats(self, filters: dict = None) -> Dict[str, Any]:
        query = (
            self.db.query(
                func.count(EqLsLeads.ID).label("total"),
                func.sum(
                    case((EqLsLeads.is_vip == 1, 1), else_=0)
                ).label("vip_count"),
            )
            .filter(EqLsLeads.status == True)
        )
        query = self._apply_filters(query, filters or {})
        result = query.one()

        total     = result.total or 0
        vip_count = result.vip_count or 0

        return {
            "vip_count":   vip_count,
            "total_leads": total,
            "vip_pct":     round(vip_count * 100.0 / total, 1) if total else 0.0,
        }
    # 1️⃣6️⃣ Lead Acquisition Rate — grouped by day/week/month


    def get_lead_acquisition_rate(self, period: str = "month", filters: dict = None) -> List[Dict[str, Any]]:
        today = date.today()
        six_months_ago = today - relativedelta(months=6)

        # Generate all months in range, then left join actual counts
        month_series = self.db.query(
            func.generate_series(
                func.date_trunc("month", func.cast(six_months_ago, Date)),
                func.date_trunc("month", func.cast(today, Date)),
                func.cast("1 month", Interval),
            ).label("month")
        ).subquery()

        lead_counts = (
            self.db.query(
                func.date_trunc("month", EqLsLeads.INQUIRY_DATE).label("month"),
                func.count(EqLsLeads.ID).label("count"),
            )
            .filter(
                EqLsLeads.status == True,
                EqLsLeads.INQUIRY_DATE.isnot(None),
                EqLsLeads.INQUIRY_DATE >= six_months_ago,
                EqLsLeads.INQUIRY_DATE <= today,
            )
            .group_by(func.date_trunc("month", EqLsLeads.INQUIRY_DATE))
            .subquery()
        )

        results = (
            self.db.query(
                func.to_char(month_series.c.month, "YYYY-MM").label("period"),
                func.coalesce(lead_counts.c.count, 0).label("count"),
            )
            .outerjoin(lead_counts, month_series.c.month == lead_counts.c.month)
            .order_by(month_series.c.month)
            .all()
        )

        rows = [{"period": r.period, "count": r.count} for r in results]
        for i, row in enumerate(rows):
            prev = rows[i - 1]["count"] if i > 0 else None
            row["growth_pct"] = (
                round((row["count"] - prev) * 100.0 / prev, 1)
                if prev and prev > 0 else None
            )
        return rows