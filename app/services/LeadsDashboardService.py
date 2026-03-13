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

    @staticmethod
    def _shape_active_inactive(data: dict) -> dict:
        total = data["total"]
        return {
            "title": "Active vs Inactive Leads",
            "units": [
                {
                    "name": "Active",
                    "value": data["active_leads"],
                    "percentage": data["active_pct"],
                },
                {
                    "name": "Inactive",
                    "value": data["inactive_leads"],
                    "percentage": data["inactive_pct"],
                },
            ]
        }
    @staticmethod
    def _shape_leads_by_type(data: list) -> dict:
        """
        Shapes lead type distribution for waffle/icon-array chart.
        Returns percentage per type for frontend rendering.
        Example: Individual 64.7%, Company 35.3%
        """
        return {
            "title": "Lead Type Distribution",
            "units": [
                {
                    "type":       row["type"],
                    "count":      row["count"],
                    "percentage": row["percentage"],
                }
                for row in data
            ]
        }

    @staticmethod
    def _shape_new_leads_periods(data: dict) -> dict:
        return {
            "title": "New Leads",
            "units": [
                {"label": "Today",      "count": data["leads_today"]},
                {"label": "This Week",  "count": data["leads_this_week"]},
                {"label": "This Month", "count": data["leads_this_month"]},
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
        
        
        #Core metrics
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

        #New metrics 
        lead_to_enquiry      = self.leads_repo.get_lead_to_enquiry_conversion(filters)
        full_funnel          = self.leads_repo.get_full_funnel_conversion(filters)
        vacant_coverage      = self.leads_repo.get_vacant_units_lead_coverage(filters)
        low_conversion_units = self.leads_repo.get_vacant_units_high_leads_low_conversion(filters)
        active_inactive      = self.leads_repo.get_active_inactive_leads_count(filters)
        new_leads_periods    = self.leads_repo.get_new_leads_periods(filters)
        leads_by_channel = self.leads_repo.get_leads_by_channel(filters)
        leads_by_type        = self.leads_repo.get_leads_by_type(filters) 
        leads_by_category = self.leads_repo.get_leads_by_category(filters)
        vip_stats = self.leads_repo.get_vip_leads_stats(filters) 
        
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
            "active_inactive":   self._shape_active_inactive(active_inactive),
            "new_leads_periods": self._shape_new_leads_periods(new_leads_periods),
            "leads_by_channel": {"title": "Leads by Channel","units": leads_by_channel,},
            "leads_by_type":       self._shape_leads_by_type(leads_by_type), 
            "leads_by_category": {"title": "Leads by Category","units": leads_by_category,},
            "vip_leads": {"title": "VIP Leads","vip_count":   vip_stats["vip_count"],"total_leads": vip_stats["total_leads"],"vip_pct":     vip_stats["vip_pct"],},
            "ratings_breakdown": self._shape_ratings_breakdown(ratings_breakdown),
            "recent_leads": self._shape_recent_leads(recent_leads),


            "last_updated": datetime.utcnow().isoformat(),
        }
    