"""
Dashboard service
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
from app.repositories.leads_repo import LeadsRepository

class LeadsDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.leads_repo = LeadsRepository(db)

    @staticmethod
    def _shape_conversion_funnel(breakdown: Dict[str, int]) -> Dict[str, Any]:
        """
        Converts any flat {stage: count} dict into block-list format.
        Fully dynamic — no hardcoded label map.
        Only renames the synthetic 'total_leads' key → 'Total Leads'.
        """
        units = []
        for key, val in breakdown.items():
            label = "Total Leads" if key == "total_leads" else key
            units.append({
                "block": label,
                "positiveValue": val,
            })
        return {
            "title": "Lead's conversion",
            "units": units,
        }
    @staticmethod
    def _shape_ratings_breakdown(ratings: list) -> dict:
        total = sum(r["lead_count"] for r in ratings)
        units = []
        for r in ratings:
            count = r["lead_count"]
            units.append({
                "name":       r["rating"],
                "value":      count,
                "percentage": round((count / total) * 100, 2) if total > 0 else 0.0,
            })
        return {
            "title": "Ratings Breakdown",
            "units": units,
        }
    
    @staticmethod
    def _shape_kpi_indicators(metrics: dict, funnel_rates: dict) -> dict:
        return {
            "title": "KPI Indicators",
            "units": [
                {
                    "label": "Total Leads",
                    "value": metrics["total_leads"],
                },
                {
                    "label": "Today's New Leads",
                    "value": metrics["todays_new_leads"],
                },
                {
                    "label": "Lead to Enquiry",
                    "value": funnel_rates["lead_to_enquiry_pct"],
                },
                {
                    "label": "Enquiry to Tenant",
                    "value": funnel_rates["enquiry_to_tenant_pct"],
                },
                {
                    "label": "Lead to Tenant",
                    "value": funnel_rates["lead_to_tenant_conversion_pct"],
                },
            ]
        }
    @staticmethod
    def _shape_recent_leads(leads: list) -> dict:
        return {
            "title": "Recent Leads",
            "headers": [
                {"title": "Leads Code",       "dataIndex": "leads_code",       "key": "leads_code"},
                {"title": "Name",             "dataIndex": "name",             "key": "name"},
                {"title": "Inquiry Date",     "dataIndex": "inquiry_date",     "key": "inquiry_date"},
                {"title": "Leads Type",       "dataIndex": "leads_type",       "key": "leads_type"},
                {"title": "Channel",          "dataIndex": "channel",          "key": "channel"},
                {"title": "Rating",           "dataIndex": "rating",           "key": "rating"},
                {"title": "Status",           "dataIndex": "status",           "key": "status"},
                {"title": "Conversion Stage", "dataIndex": "conversion_stage", "key": "conversion_stage"},
                {"title": "Property ID",      "dataIndex": "property_id",      "key": "property_id"},
                {"title": "Property Unit",    "dataIndex": "property_unit",    "key": "property_unit"},
                {"title": "Created By",       "dataIndex": "created_by",       "key": "created_by"},
            ],
            "units": leads,
        }
    
    @staticmethod
    def _shape_lead_funnel_rates(metrics: dict, funnel_rates: dict) -> dict:
        total_leads = metrics["total_leads"]
        enquiry = funnel_rates["converted_to_enquiry"]
        tenant = funnel_rates["converted_to_tenant"]

        return {
            "title": "Lead Conversion ",
            "units": [
                {
                    "name": "Total Leads",
                    "value": f"{total_leads:,}"
                },
                {
                    "name": "Enquiry",
                    "value": f"{enquiry:,}",
                    "percentage": f'{funnel_rates["lead_to_enquiry_pct"]}% Conv.'
                },
                {
                    "name": "Tenant",
                    "value": f"{tenant:,}",
                    "percentage": f'{funnel_rates["lead_to_tenant_conversion_pct"]}% Conv.'
                },
             
            ]
        }





    def get_dashboard_data(self,property_id: int = None,property_type: str = None,date_from: str = None,date_to: str = None,) -> Dict[str, Any]:
        """Get full dashboard data"""
        filters = {
        "property_id":   property_id,
        "property_type": property_type,
        "date_from":     date_from,
        "date_to":       date_to,
    }
        
        
        # ── Core metrics ──────────────────────────────────
        total_leads          = self.leads_repo.get_total_leads_live(filters)
        todays_new_leads     = self.leads_repo.get_todays_new_leads_live(filters)
        conversion_breakdown = self.leads_repo.get_conversion_breakdown_live(filters)
        ratings_breakdown    = self.leads_repo.get_leads_by_ratings_live(filters)
        recent_leads         = self.leads_repo.get_recent_leads_live(limit=10,filters=filters)

        converted = conversion_breakdown.get("Convert to Tenant", 0)
        if total_leads > 0:
            conversion_rate = round((int(converted) / int(total_leads)) * 100, 2)
        else:
            conversion_rate = 0.0

        # ── New metrics ───────────────────────────────────
        lead_to_enquiry      = self.leads_repo.get_lead_to_enquiry_conversion(filters)
        full_funnel          = self.leads_repo.get_full_funnel_conversion(filters)
        vacant_coverage      = self.leads_repo.get_vacant_units_lead_coverage(filters)
        low_conversion_units = self.leads_repo.get_vacant_units_high_leads_low_conversion(filters)
        metrics_data = {
                "total_leads":      total_leads,
                "todays_new_leads": todays_new_leads,
                "converted_leads":  converted,
                "conversion_rate":  conversion_rate,
            }
        

        funnel_rates_data = {
                "lead_to_enquiry_pct":           full_funnel["lead_to_enquiry_pct"],
                "enquiry_to_tenant_pct":         full_funnel["enquiry_to_tenant_pct"],
                "lead_to_tenant_conversion_pct": full_funnel["lead_to_tenant_conversion_pct"],
                "converted_to_enquiry":          lead_to_enquiry["converted_to_enquiry"],
                "converted_to_tenant":           full_funnel["converted_to_tenant"],
            }        






        return {
            "metrics": {
                "total_leads":      total_leads,
                "todays_new_leads": todays_new_leads,
                "converted_leads":  converted,
                "conversion_rate":  conversion_rate,
            },
            "conversion_funnel": self._shape_conversion_funnel(conversion_breakdown),
            "kpi_indicators":    self._shape_kpi_indicators(metrics_data, funnel_rates_data), 
            "lead_funnel_rates": self._shape_lead_funnel_rates(metrics_data, funnel_rates_data),
            # "funnel_rates": {
            #     "lead_to_enquiry_pct":           full_funnel["lead_to_enquiry_pct"],
            #     "enquiry_to_tenant_pct":         full_funnel["enquiry_to_tenant_pct"],
            #     "lead_to_tenant_conversion_pct": full_funnel["lead_to_tenant_conversion_pct"],
            #     "converted_to_enquiry":          lead_to_enquiry["converted_to_enquiry"],
            #     "converted_to_tenant":           full_funnel["converted_to_tenant"],
            # },
            "vacant_unit_coverage":  vacant_coverage,
            "low_conversion_units":  low_conversion_units,
            "ratings_breakdown": self._shape_ratings_breakdown(ratings_breakdown),
            "recent_leads": self._shape_recent_leads(recent_leads),

            "last_updated": datetime.utcnow().isoformat(),
        }