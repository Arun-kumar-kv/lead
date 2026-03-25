# from sqlalchemy.orm import Session
# from datetime import datetime
# from typing import Dict, Any
# from app.repositories.leads_repo import LeadsRepository

# class LeadsDashboardService:
#     def __init__(self, db: Session):
#         self.db = db
#         self.leads_repo = LeadsRepository(db)
#     @staticmethod
#     def _shape_conversion_funnel(breakdown: Dict[str, int]) -> Dict[str, Any]:
#         FUNNEL_ORDER = ["total_leads", "Engaged Lead", "Convert to Enquiry", "Convert to Tenant"]

#         ordered = sorted(
#             breakdown.items(),
#             key=lambda x: FUNNEL_ORDER.index(x[0]) if x[0] in FUNNEL_ORDER else 99
#         )

#         units = []
#         for key, val in ordered:
#             label = "Total Leads" if key == "total_leads" else key
#             units.append({
#                 "block": label,
#                 "positiveValue": val,
#             })

#         return {
#             "title": "Lead's Status",
#             "type":  "Conversion funnel",
#             "units": units,
#         }
#     # @staticmethod
#     # def _shape_conversion_funnel(breakdown: Dict[str, int]) -> Dict[str, Any]:
#     #     """
#     #     Converts any flat {stage: count} dict into block-list format.
#     #     Fully dynamic — no hardcoded label map.
#     #     Only renames the synthetic 'total_leads' key → 'Total Leads'.
#     #     """
#     #     units = []
#     #     for key, val in breakdown.items():
#     #         label = "Total Leads" if key == "total_leads" else key
#     #         units.append({
#     #             "block": label,
#     #             "positiveValue": val,
#     #         })
#     #     return {
#     #         "title": "Lead's conversion",
#     #         "units": units,
#     #     }
#     @staticmethod
#     def _shape_ratings_breakdown(ratings: list) -> dict:
#         total = sum(r["lead_count"] for r in ratings)
#         units = []
#         for r in ratings:
#             count = r["lead_count"]
#             units.append({
#                 "name":       r["rating"],
#                 "value":      count,
#                 "percentage": round((count / total) * 100, 2) if total > 0 else 0.0,
#             })
#         return {
#             "title": "Ratings Breakdown",
#             "type":"Radar / Spider chart ",
#             "units": units,
#         }
#     @staticmethod
#     def _shape_new_leads_periods(data: dict) -> dict:
#         return {
#             "title": "New Leads",
#             "type": "KPI Cards",
#             "summary": {
#                 "label": "This Month",
#                 "count": data["leads_this_month"]
#             },
#             "detail": {
#                 "today": {
#                     "label": "Today",
#                     "count": data["leads_today"]
#                 },
#                 "this_week": {
#                     "label": "This Week",
#                     "count": data["leads_this_week"]
#                 },
#                 "this_month": {
#                     "label": "This Month",
#                     "count": data["leads_this_month"]
#                 }
#             }
#         }
#     # @staticmethod
#     # def _shape_kpi_indicators(metrics: dict, funnel_rates: dict) -> dict:
#     #     return {
#     #         "title": "KPI Indicators",
#     #         "units": [
#     #             {
#     #                 "label": "Total Leads",
#     #                 "value": metrics["total_leads"],
#     #             },
#     #             {
#     #                 "label": "Today's New Leads",
#     #                 "value": metrics["todays_new_leads"],
#     #             },
#     #             {
#     #                 "label": "Lead to Enquiry",
#     #                 "value": funnel_rates["lead_to_enquiry_pct"],
#     #             },
#     #             {
#     #                 "label": "Enquiry to Tenant",
#     #                 "value": funnel_rates["enquiry_to_tenant_pct"],
#     #             },
#     #             {
#     #                 "label": "Lead to Tenant",
#     #                 "value": funnel_rates["lead_to_tenant_conversion_pct"],
#     #             },
#     #         ]
#     #     }
#     @staticmethod
#     def _shape_recent_leads(leads: list) -> dict:
#         return {
#             "title": "Recent Leads",
#             "type":"Data table",
#             "headers": [
#                 {"title": "Leads Code",       "dataIndex": "leads_code",       "key": "leads_code"},
#                 {"title": "Name",             "dataIndex": "name",             "key": "name"},
#                 {"title": "Inquiry Date",     "dataIndex": "inquiry_date",     "key": "inquiry_date"},
#                 {"title": "Leads Type",       "dataIndex": "leads_type",       "key": "leads_type"},
#                 {"title": "Channel",          "dataIndex": "channel",          "key": "channel"},
#                 {"title": "Rating",           "dataIndex": "rating",           "key": "rating"},
#                 {"title": "Status",           "dataIndex": "status",           "key": "status"},
#                 {"title": "Conversion Stage", "dataIndex": "conversion_stage", "key": "conversion_stage"},
#                 {"title": "Property ID",      "dataIndex": "property_id",      "key": "property_id"},
#                 {"title": "Property Unit",    "dataIndex": "property_unit",    "key": "property_unit"},
#                 {"title": "Created By",       "dataIndex": "created_by",       "key": "created_by"},
#             ],
#             "units": leads,
#         }
    
#     @staticmethod
#     def _shape_lead_funnel_rates(metrics: dict, funnel_rates: dict) -> dict:
#         total_leads = metrics["total_leads"]
#         enquiry = funnel_rates["converted_to_enquiry"]
#         tenant = funnel_rates["converted_to_tenant"]

#         return {
#             "title": "Lead Conversion ",
#             "type":"Process Flow Funnel/horizontal funnel",
#             "units": [
#                 {
#                     "name": "Total Leads",
#                     "value": f"{total_leads:,}"
#                 },
#                 {
#                     "name": "Enquiry",
#                     "value": f"{enquiry:,}",
#                     "percentage": f'{funnel_rates["lead_to_enquiry_pct"]}% Conv.'
#                 },
#                 {
#                     "name": "Tenant",
#                     "value": f"{tenant:,}",
#                     "percentage": f'{funnel_rates["lead_to_tenant_conversion_pct"]}% Conv.'
#                 },
             
#             ]
#         }

#     @staticmethod
#     def _shape_active_inactive(data: dict) -> dict:
#         total = data["total"]
#         return {
#             "title": "Active vs Inactive Leads",
#             "type":"Donut chart",
#             "units": [
#                 {
#                     "name": "Active",
#                     "value": data["active_leads"],
#                     "percentage": data["active_pct"],
#                 },
#                 {
#                     "name": "Inactive",
#                     "value": data["inactive_leads"],
#                     "percentage": data["inactive_pct"],
#                 },
#             ]
#         }
#     @staticmethod
#     def _shape_leads_by_type(data: list) -> dict:
#         """
#         Shapes lead type distribution for waffle/icon-array chart.
#         Returns percentage per type for frontend rendering.
#         Example: Individual 64.7%, Company 35.3%
#         """
#         return {
#             "title": "Lead Type Distribution",
#             "type":"Waffle / icon-array chart",
#             "units": [
#                 {
#                     "type":       row["type"],
#                     "count":      row["count"],
#                     "percentage": row["percentage"],
#                 }
#                 for row in data
#             ]
#         }

#     # @staticmethod
#     # def _shape_new_leads_periods(data: dict) -> dict:
#     #     return {
#     #         "title": "New Leads",
#     #         "type":"KPI Cards",
#     #         "units": [
#     #             {"label": "Today",      "count": data["leads_today"]},
#     #             {"label": "This Week",  "count": data["leads_this_week"]},
#     #             {"label": "This Month", "count": data["leads_this_month"]},
#     #         ]
#     #     }
#     @staticmethod
#     def _shape_leads_by_channel(data: list) -> dict:
#         return {
#             "title": "Leads by Channel",
#             "type":" Horizontal bar chart",                  
#             "units": [
#                 {"channel": row["channel"], "count": row["count"]}
#                 for row in data
#             ]
#         }
#     @staticmethod
#     def _shape_acquisition_rate(data: list) -> dict:
#         return {
#             "title":  "Lead Acquisition Rate",
#             "type":" Line / area chart ",
#             "units": [
#                 {
#                     "period":     row["period"],
#                     "count":      row["count"],
#                     "growth_pct": row["growth_pct"],
#                 }
#                 for row in data
#             ]
#         }
#     @staticmethod
#     def _shape_vacant_unit_coverage(data: dict) -> dict:
#         total   = data.get("total", 0)
#         covered = data.get("value", 0)
#         pct     = round((covered / total) * 100, 2) if total > 0 else 0.0
#         if pct >= 50:
#             status, color = "Sufficient",    "green"
#         elif pct >= 20:
#             status, color = "Moderate",      "orange"
#         else:
#             status, color = "Insufficient",  "red"
#         return {
#             "title":        "Lead Coverage of Vacant Units",
#             "type":         "Progress / coverage card",
#             "total":        total,
#             "value":        covered,
#             "percentage":   pct,
#             "status":       status,
#             "status_color": color,
#             "display_text": f"{covered} / {total} units",
#         }
#     def get_dashboard_data(self,property_id: int = None,property_type: str = None,date_from: str = None,date_to: str = None,) -> Dict[str, Any]:
#         """Get full dashboard data"""
#         filters = {
#         "property_id":   property_id,
#         "property_type": property_type,
#         "date_from":     date_from,
#         "date_to":       date_to,
#     }
        
        
#         #Core metrics
#         total_leads          = self.leads_repo.get_total_leads_live(filters)
#         todays_new_leads     = self.leads_repo.get_todays_new_leads_live(filters)
#         conversion_breakdown = self.leads_repo.get_conversion_breakdown_live(filters)
#         ratings_breakdown    = self.leads_repo.get_leads_by_ratings_live(filters)
#         recent_leads         = self.leads_repo.get_recent_leads_live(limit=10,filters=filters)

#         converted = conversion_breakdown.get("Convert to Tenant", 0)
#         if total_leads > 0:
#             conversion_rate = round((int(converted) / int(total_leads)) * 100, 2)
#         else:
#             conversion_rate = 0.0

#         #New metrics 
#         lead_to_enquiry      = self.leads_repo.get_lead_to_enquiry_conversion(filters)
#         full_funnel          = self.leads_repo.get_full_funnel_conversion(filters)
#         vacant_coverage      = self.leads_repo.get_vacant_units_lead_coverage(filters)
#         low_conversion_units = self.leads_repo.get_vacant_units_high_leads_low_conversion(filters)
#         active_inactive      = self.leads_repo.get_active_inactive_leads_count(filters)
#         new_leads_periods    = self.leads_repo.get_new_leads_periods(filters)
#         leads_by_channel = self.leads_repo.get_leads_by_channel(filters)
#         leads_by_type        = self.leads_repo.get_leads_by_type(filters) 
#         leads_by_category = self.leads_repo.get_leads_by_category(filters)
#         vip_stats = self.leads_repo.get_vip_leads_stats(filters) 
#         acquisition_rate = self.leads_repo.get_lead_acquisition_rate(period="month", filters=filters)
        
#         metrics_data = {
#                 "total_leads":      total_leads,
#                 "todays_new_leads": todays_new_leads,
#                 "converted_leads":  converted,
#                 "conversion_rate":  conversion_rate,
#             }
        

#         funnel_rates_data = {
#                 "lead_to_enquiry_pct":           full_funnel["lead_to_enquiry_pct"],
#                 "enquiry_to_tenant_pct":         full_funnel["enquiry_to_tenant_pct"],
#                 "lead_to_tenant_conversion_pct": full_funnel["lead_to_tenant_conversion_pct"],
#                 "converted_to_enquiry":          lead_to_enquiry["converted_to_enquiry"],
#                 "converted_to_tenant":           full_funnel["converted_to_tenant"],
#             }        

#         return {
#             "total_lead_kpi": {
#                 "title":"Total_leads",
#                 "type": "KPI Cards",
#                 "summary": {
#                 "label": "Total Leads",
#                 "count": total_leads,
#                 }
#             #     "todays_new_leads": todays_new_leads,
#             #     "converted_leads":  converted,
#             #     "conversion_rate":  conversion_rate,
#             },
#             "conversion_funnel": self._shape_conversion_funnel(conversion_breakdown),
#             # "kpi_indicators":    self._shape_kpi_indicators(metrics_data, funnel_rates_data), 
#             "lead_funnel_rates": self._shape_lead_funnel_rates(metrics_data, funnel_rates_data),
#             # "funnel_rates": {
#             #     "lead_to_enquiry_pct":           full_funnel["lead_to_enquiry_pct"],
#             #     "enquiry_to_tenant_pct":         full_funnel["enquiry_to_tenant_pct"],
#             #     "lead_to_tenant_conversion_pct": full_funnel["lead_to_tenant_conversion_pct"],
#             #     "converted_to_enquiry":          lead_to_enquiry["converted_to_enquiry"],
#             #     "converted_to_tenant":           full_funnel["converted_to_tenant"],
#             # },
#             "vacant_unit_coverage":  self._shape_vacant_unit_coverage(vacant_coverage),
#             "low_conversion_units":  low_conversion_units,
#             "active_inactive":   self._shape_active_inactive(active_inactive),
#             "new_leads_periods": self._shape_new_leads_periods(new_leads_periods),
#             "leads_by_channel": self._shape_leads_by_channel(leads_by_channel),
#             "leads_by_type":       self._shape_leads_by_type(leads_by_type), 
#             "leads_by_category": {"title": "Leads by Category","type":"Donut chart","units": leads_by_category,},
#             "lead_acquisition_rate": self._shape_acquisition_rate(acquisition_rate),
#             "vip_leads": {"title": "VIP Leads","type":"Badge card","vip_count":   vip_stats["vip_count"],"total_leads": vip_stats["total_leads"],"vip_pct":     vip_stats["vip_pct"],},
#             "ratings_breakdown": self._shape_ratings_breakdown(ratings_breakdown),
#             "recent_leads": self._shape_recent_leads(recent_leads),


#             "last_updated": datetime.utcnow().isoformat(),
#         }
#######################
"""
Dashboard service
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
import asyncio
import hashlib
import json
from dataclasses import dataclass
from app.repositories.leads_repo import LeadsRepository


# Filters Dataclass 
@dataclass
class DashboardFilters:
    property_id:   int | None = None
    property_type: str | None = None
    date_from:     str | None = None
    date_to:       str | None = None

    def to_dict(self) -> dict:
        return {
            "property_id":   self.property_id,
            "property_type": self.property_type,
            "date_from":     self.date_from,
            "date_to":       self.date_to,
        }

    def cache_key(self) -> str:
        hash_val = hashlib.md5(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()
        return f"dashboard:{hash_val}"


#  Service 
class LeadsDashboardService:
    CACHE_TTL = 300  # 5 minutes

    def __init__(self, db: Session, redis_client=None, session_factory=None):
        self.db          = db
        self.leads_repo  = LeadsRepository(db)
        self.redis       = redis_client  # optional, pass None to skip caching
        self.session_factory = session_factory 

    #  Shaping Methods 

    @staticmethod
    def _shape_total_leads_kpi(total_leads: int) -> dict:
        return {
            "title":   "Total Leads",
            "type":    "KPI Cards",
            "summary": {
                "label": "Total Leads",
                "count": total_leads,
            }
        }

    @staticmethod
    def _shape_conversion_funnel(breakdown: Dict[str, int]) -> Dict[str, Any]:
        FUNNEL_ORDER = ["total_leads", "Engaged Lead", "Convert to Enquiry", "Convert to Tenant"]
        ordered = sorted(
            breakdown.items(),
            key=lambda x: FUNNEL_ORDER.index(x[0]) if x[0] in FUNNEL_ORDER else 99
        )
        return {
            "title": "Lead's Status",
            "type":  "Conversion funnel",
            "units": [
                {"block": "Total Leads" if k == "total_leads" else k, "positiveValue": v}
                for k, v in ordered
            ],
        }

    @staticmethod
    def _shape_ratings_breakdown(ratings: list) -> dict:
        total = sum(r["lead_count"] for r in ratings)
        return {
            "title": "Ratings Breakdown",
            "type":  "Radar / Spider chart",
            "units": [
                {
                    "name":       r["rating"],
                    "value":      r["lead_count"],
                    "percentage": round((r["lead_count"] / total) * 100, 2) if total > 0 else 0.0,
                }
                for r in ratings
            ],
        }

    @staticmethod
    def _shape_new_leads_periods(data: dict) -> dict:
        return {
            "title":   "New Leads",
            "type":    "KPI Cards",
            "summary": {"label": "This Month", "count": data["leads_this_month"]},
            "detail": {
                "today":      {"label": "Today",      "count": data["leads_today"]},
                "this_week":  {"label": "This Week",  "count": data["leads_this_week"]},
                "this_month": {"label": "This Month", "count": data["leads_this_month"]},
            },
        }

    @staticmethod
    def _shape_recent_leads(leads: list) -> dict:
        return {
            "title":   "Recent Leads",
            "type":    "Data table",
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
        return {
            "title": "Lead Conversion",
            "type":  "Process Flow Funnel/horizontal funnel",
            "units": [
                {
                    "name":  "Total Leads",
                    "value": f"{metrics['total_leads']:,}",
                },
                {
                    "name":       "Enquiry",
                    "value":      f"{funnel_rates['converted_to_enquiry']:,}",
                    "percentage": f"{funnel_rates['lead_to_enquiry_pct']}% Conv.",
                },
                {
                    "name":       "Tenant",
                    "value":      f"{funnel_rates['converted_to_tenant']:,}",
                    "percentage": f"{funnel_rates['lead_to_tenant_conversion_pct']}% Conv.",
                },
            ],
        }

    @staticmethod
    def _shape_active_inactive(data: dict) -> dict:
        return {
            "title": "Active vs Inactive Leads",
            "type":  "Donut chart",
            "units": [
                {"name": "Active",   "value": data["active_leads"],   "percentage": data["active_pct"]},
                {"name": "Inactive", "value": data["inactive_leads"], "percentage": data["inactive_pct"]},
            ],
        }

    @staticmethod
    def _shape_leads_by_type(data: list) -> dict:
        return {
            "title": "Lead Type Distribution",
            "type":  "Waffle / icon-array chart",
            "units": [
                {"type": row["type"], "count": row["count"], "percentage": row["percentage"]}
                for row in data
            ],
        }

    # @staticmethod
    # def _shape_leads_by_channel(data: list) -> dict:
    #     return {
    #         "title": "Leads by Channel",
    #         "type":  "Horizontal bar chart",
    #         "units": [
    #             {"channel": row["channel"], "count": row["count"]}
    #             for row in data
    #         ],
    #     }
    @staticmethod
    def _shape_leads_by_channel(data: list) -> dict:
        sorted_data = sorted(data, key=lambda x: x["count"], reverse=True)
        total = sum(row["count"] for row in sorted_data)

        units = []
        for i, row in enumerate(sorted_data):
            unit = {
                "rank":       i + 1,
                "channel":    row["channel"],
                "count":      row["count"],
                "percentage": round((row["count"] / total) * 100, 1) if total > 0 else 0.0,
                "is_top5":    i < 5,
            }
            units.append(unit)

        top5 = units[:5]
        rest_count = sum(r["count"] for r in units[5:])

        return {
            "title":        "Leads by Channel",
            "type":         "Bubble chart",
            "total_leads":  total,
            "total_channels": len(units),
            "summary": {
                "top5":  top5,

            },
            "detail": units,
        }
    @staticmethod
    def _shape_acquisition_rate(data: list) -> dict:
        return {
            "title": "Lead Acquisition Rate",
            "type":  "Line / area chart",
            "units": [
                {"period": row["period"], "count": row["count"], "growth_pct": row["growth_pct"]}
                for row in data
            ],
        }

    @staticmethod
    def _shape_vacant_unit_coverage(data: dict) -> dict:
        total   = data.get("total", 0)
        covered = data.get("value", 0)
        pct     = round((covered / total) * 100, 2) if total > 0 else 0.0
        if pct >= 50:
            status, color = "Sufficient",   "green"
        elif pct >= 20:
            status, color = "Moderate",     "orange"
        else:
            status, color = "Insufficient", "red"
        return {
            "title":        "Lead Coverage of Vacant Units",
            "type":         "Progress / coverage card",
            "total":        total,
            "value":        covered,
            "percentage":   pct,
            "status":       status,
            "status_color": color,
            "display_text": f"{covered} / {total} units",
        }

    #  Cache Helpers 

    def _get_cache(self, key: str):
        if not self.redis:
            print("Redis not configured — caching disabled")
            return None
        cached = self.redis.get(key)
        if cached:
            print("Cache HIT")
            return json.loads(cached)
        print("Cache MISS — hitting DB")
        return None

    def _set_cache(self, key: str, data: dict):
        if not self.redis:
            return
        self.redis.setex(key, self.CACHE_TTL, json.dumps(data, default=str))

    def invalidate_cache(self):
        """Call this when a lead is created/updated/deleted."""
        if not self.redis:
            return
        keys = self.redis.keys("dashboard:*")
        if keys:
            self.redis.delete(*keys)

    #  Data Fetching (Parallel) 

    def _fetch_all(self, filters: dict) -> dict:
        def run(fn):
            if self.session_factory:
                session = self.session_factory()
                try:
                    repo = LeadsRepository(session)
                    return fn(repo)
                finally:
                    session.close()
            else:
                return fn(self.leads_repo)  # fallback: no parallelism

        tasks = {
            "total_leads":          lambda repo: repo.get_total_leads_live(filters),
            "todays_new_leads":     lambda repo: repo.get_todays_new_leads_live(filters),
            "conversion_breakdown": lambda repo: repo.get_conversion_breakdown_live(filters),
            "ratings_breakdown":    lambda repo: repo.get_leads_by_ratings_live(filters),
            "recent_leads":         lambda repo: repo.get_recent_leads_live(limit=10, filters=filters),
            "lead_to_enquiry":      lambda repo: repo.get_lead_to_enquiry_conversion(filters),
            "full_funnel":          lambda repo: repo.get_full_funnel_conversion(filters),
            "vacant_coverage":      lambda repo: repo.get_vacant_units_lead_coverage(filters),
            "low_conversion_units": lambda repo: repo.get_vacant_units_high_leads_low_conversion(filters),
            "active_inactive":      lambda repo: repo.get_active_inactive_leads_count(filters),
            "new_leads_periods":    lambda repo: repo.get_new_leads_periods(filters),
            "leads_by_channel":     lambda repo: repo.get_leads_by_channel(filters),
            "leads_by_type":        lambda repo: repo.get_leads_by_type(filters),
            "leads_by_category":    lambda repo: repo.get_leads_by_category(filters),
            "vip_stats":            lambda repo: repo.get_vip_leads_stats(filters),
            "acquisition_rate":     lambda repo: repo.get_lead_acquisition_rate(period="month", filters=filters),
        }

        results = {}
        with ThreadPoolExecutor() as executor:
            futures = {key: executor.submit(run, fn) for key, fn in tasks.items()}
            for key, future in futures.items():
                results[key] = future.result()

        return results

    #  Main Entry Point 

    def get_dashboard_data(
        self,
        property_id:   int = None,
        property_type: str = None,
        date_from:     str = None,
        date_to:       str = None,
    ) -> Dict[str, Any]:

        f = DashboardFilters(property_id, property_type, date_from, date_to)

        # ① Check cache
        cached = self._get_cache(f.cache_key())
        if cached:
            return cached

        # ② Fetch all data in parallel
        r = self._fetch_all(f.to_dict())

        # ③ Derived values
        converted = r["conversion_breakdown"].get("Convert to Tenant", 0)
        conversion_rate = round((int(converted) / int(r["total_leads"])) * 100, 2) if r["total_leads"] > 0 else 0.0

        metrics_data = {
            "total_leads":      r["total_leads"],
            "todays_new_leads": r["todays_new_leads"],
            "converted_leads":  converted,
            "conversion_rate":  conversion_rate,
        }

        funnel_rates_data = {
            "lead_to_enquiry_pct":           r["full_funnel"]["lead_to_enquiry_pct"],
            "enquiry_to_tenant_pct":         r["full_funnel"]["enquiry_to_tenant_pct"],
            "lead_to_tenant_conversion_pct": r["full_funnel"]["lead_to_tenant_conversion_pct"],
            "converted_to_enquiry":          r["lead_to_enquiry"]["converted_to_enquiry"],
            "converted_to_tenant":           r["full_funnel"]["converted_to_tenant"],
        }

        # ④ Shape and return
        data = {
            "total_lead_kpi":        self._shape_total_leads_kpi(r["total_leads"]),
            "conversion_funnel":     self._shape_conversion_funnel(r["conversion_breakdown"]),
            "lead_funnel_rates":     self._shape_lead_funnel_rates(metrics_data, funnel_rates_data),
            "vacant_unit_coverage":  self._shape_vacant_unit_coverage(r["vacant_coverage"]),
            "low_conversion_units":  r["low_conversion_units"],
            "active_inactive":       self._shape_active_inactive(r["active_inactive"]),
            "new_leads_periods":     self._shape_new_leads_periods(r["new_leads_periods"]),
            "leads_by_channel":      self._shape_leads_by_channel(r["leads_by_channel"]),
            "leads_by_type":         self._shape_leads_by_type(r["leads_by_type"]),
            "leads_by_category":     {"title": "Leads by Category", "type": "Donut chart", "units": r["leads_by_category"]},
            "lead_acquisition_rate": self._shape_acquisition_rate(r["acquisition_rate"]),
            "vip_leads":             {"title": "VIP Leads", "type": "Badge card", "vip_count": r["vip_stats"]["vip_count"], "total_leads": r["vip_stats"]["total_leads"], "vip_pct": r["vip_stats"]["vip_pct"]},
            "ratings_breakdown":     self._shape_ratings_breakdown(r["ratings_breakdown"]),
            "recent_leads":          self._shape_recent_leads(r["recent_leads"]),
            "last_updated":          datetime.utcnow().isoformat(),
        }

        # ⑤ Store in cache
        self._set_cache(f.cache_key(), data)

        return data 