"""
Dashboard service - FIXED VERSION
Direct calculation of conversion rate
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
from app.repositories.leads_repo import LeadsRepository


class LeadsDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.leads_repo = LeadsRepository(db)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data with correct conversion rate"""

        # Get all data
        total_leads = self.leads_repo.get_total_leads_live()
        todays_new_leads = self.leads_repo.get_todays_new_leads_live()
        conversion_breakdown = self.leads_repo.get_conversion_breakdown_live()
        ratings_breakdown = self.leads_repo.get_leads_by_ratings_live()
        recent_leads = self.leads_repo.get_recent_leads_live(limit=10)

        # Get converted count from breakdown
        # converted = conversion_breakdown.get("converted_to_tenant", 0)
        converted = conversion_breakdown.get("Convert to Tenant", 0)
        print("total_lead",total_leads)
        print("converted",converted)
        # Calculate conversion rate
        if total_leads > 0:
            conversion_rate = (int(converted) / int(total_leads)) * 100
            conversion_rate = round(conversion_rate, 2)
            print("conversion_rate",conversion_rate)
        else:
            conversion_rate = 0.0
         # ── New metrics ───────────────────────────────────
        lead_to_enquiry      = self.leads_repo.get_lead_to_enquiry_conversion()
        full_funnel          = self.leads_repo.get_full_funnel_conversion()
        vacant_coverage      = self.leads_repo.get_vacant_units_lead_coverage()
        low_conversion_units = self.leads_repo.get_vacant_units_high_leads_low_conversion()

        return {
            "metrics": {
                "total_leads": total_leads,
                "todays_new_leads": todays_new_leads,
                "converted_leads": converted,
                "conversion_rate": conversion_rate,
            },
            "conversion_funnel": conversion_breakdown,
            "funnel_rates": {
                "lead_to_enquiry_pct":          full_funnel["lead_to_enquiry_pct"],
                "enquiry_to_tenant_pct":        full_funnel["enquiry_to_tenant_pct"],
                "lead_to_tenant_conversion_pct": full_funnel["lead_to_tenant_conversion_pct"],
                "converted_to_enquiry":         lead_to_enquiry["converted_to_enquiry"],
                "converted_to_tenant":          full_funnel["converted_to_tenant"],
            },
            "vacant_unit_coverage":  vacant_coverage,
            "low_conversion_units":  low_conversion_units,
            "ratings_breakdown": ratings_breakdown,
            "recent_activity": {
                "recent_leads": recent_leads
            },
            "last_updated": datetime.utcnow().isoformat()
        }