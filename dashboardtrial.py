# # """
# # TERP_LEADS Analytics Dashboard - Premium UI (Fixed Production Version)

# # Run:
# # streamlit run streamlit_dashboard_standalone.py
# # """

# # import streamlit as st
# # import requests
# # import plotly.graph_objects as go
# # import pandas as pd
# # from datetime import datetime
# # import time

# # # =====================================
# # # CONFIG
# # # =====================================

# # API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# # st.set_page_config(
# #     page_title="TERP Leads Analytics",
# #     page_icon="📊",
# #     layout="wide"
# # )

# # # =====================================
# # # PREMIUM DARK UI STYLING
# # # =====================================

# # st.markdown("""
# # <style>
# # .stApp {
# #     background-color: #0f172a;
# #     color: #e2e8f0;
# # }

# # .main-header {
# #     font-size: 2.4rem;
# #     font-weight: 700;
# #     background: linear-gradient(90deg, #38bdf8, #818cf8);
# #     -webkit-background-clip: text;
# #     -webkit-text-fill-color: transparent;
# #     margin-bottom: 1.5rem;
# # }

# # .section-header {
# #     font-size: 1.3rem;
# #     font-weight: 600;
# #     margin-top: 2rem;
# #     margin-bottom: 1rem;
# #     padding-bottom: 0.4rem;
# #     border-bottom: 1px solid rgba(148,163,184,0.2);
# # }

# # [data-testid="stMetric"] {
# #     background: linear-gradient(145deg, #1e293b, #0f172a);
# #     padding: 20px;
# #     border-radius: 14px;
# #     border: 1px solid rgba(148,163,184,0.1);
# #     box-shadow: 0 4px 20px rgba(0,0,0,0.4);
# # }

# # section[data-testid="stSidebar"] {
# #     background-color: #0f172a;
# #     border-right: 1px solid rgba(148,163,184,0.1);
# # }
# # </style>
# # """, unsafe_allow_html=True)

# # # =====================================
# # # API CALLS
# # # =====================================

# # @st.cache_data(ttl=30)
# # def fetch_leads_dashboard():
# #     try:
# #         r = requests.get(f"{API_BASE_URL}/leads-dashboard/", timeout=10)
# #         r.raise_for_status()
# #         return r.json()
# #     except Exception as e:
# #         st.error(f"Leads API Error: {e}")
# #         return None


# # @st.cache_data(ttl=30)
# # def fetch_vacancy_dashboard():
# #     try:
# #         r = requests.get(f"{API_BASE_URL}/vacancy-dashboard/", timeout=10)
# #         r.raise_for_status()
# #         return r.json()
# #     except Exception as e:
# #         st.error(f"Vacancy API Error: {e}")
# #         return None


# # @st.cache_data(ttl=15)
# # def fetch_recent_leads(limit=20):
# #     try:
# #         r = requests.get(
# #             f"{API_BASE_URL}/leads-dashboard/live/recent",
# #             params={"limit": limit},
# #             timeout=10
# #         )
# #         r.raise_for_status()
# #         return r.json().get("recent_leads", [])
# #     except Exception:
# #         return []

# # # =====================================
# # # CHART UTILITIES
# # # =====================================

# # def empty_chart(title):
# #     fig = go.Figure()
# #     fig.update_layout(
# #         paper_bgcolor="#0f172a",
# #         plot_bgcolor="#0f172a",
# #         font=dict(color="white"),
# #         height=420,
# #         title=title
# #     )
# #     return fig


# # # =====================================
# # # LEADS CHARTS
# # # =====================================

# # def create_funnel_chart(data):
# #     if not data:
# #         return empty_chart("Lead Conversion Funnel")

# #     mapping = [
# #         ("New Lead", data.get("New Lead", 0)),
# #         ("Prospect", data.get("Prospect", 0)),
# #         ("Opportunity", data.get("Opportunity", 0)),
# #         ("Converted", data.get("Convert to Tenant", 0)),
# #     ]

# #     filtered = [x for x in mapping if x[1] > 0]
# #     if not filtered:
# #         return empty_chart("Lead Conversion Funnel")

# #     stages = [x[0] for x in filtered]
# #     values = [x[1] for x in filtered]

# #     fig = go.Figure(go.Funnel(
# #         y=stages,
# #         x=values,
# #         textinfo="value+percent total"
# #     ))

# #     fig.update_layout(
# #         paper_bgcolor="#0f172a",
# #         plot_bgcolor="#0f172a",
# #         font=dict(color="white"),
# #         height=420,
# #         title="Lead Conversion Funnel"
# #     )

# #     return fig


# # def create_ratings_chart(data):
# #     if not data:
# #         return empty_chart("Lead Ratings Distribution")

# #     labels = [r.get("rating", "Unknown") for r in data]
# #     values = [r.get("lead_count", 0) for r in data]

# #     fig = go.Figure(go.Pie(
# #         labels=labels,
# #         values=values,
# #         hole=0.55,
# #         textinfo="percent+label"
# #     ))

# #     fig.update_layout(
# #         paper_bgcolor="#0f172a",
# #         plot_bgcolor="#0f172a",
# #         font=dict(color="white"),
# #         height=420,
# #         title="Lead Ratings Distribution"
# #     )

# #     return fig


# # # =====================================
# # # VACANCY CHARTS
# # # =====================================

# # def create_vacancy_trend_chart(data):

# #     if isinstance(data, dict) and "data" in data:
# #         data = data["data"]

# #     if not isinstance(data, list) or not data:
# #         return empty_chart("Vacancy Rate Trend")

# #     months = [x.get("month") for x in data]
# #     occupied = [x.get("occupied_units", 0) for x in data]
# #     vacant = [x.get("vacant_units", 0) for x in data]

# #     fig = go.Figure()
# #     fig.add_bar(x=months, y=occupied, name="Occupied")
# #     fig.add_bar(x=months, y=vacant, name="Vacant")

# #     fig.update_layout(
# #         barmode="stack",
# #         paper_bgcolor="#0f172a",
# #         plot_bgcolor="#0f172a",
# #         font=dict(color="white"),
# #         height=420,
# #         title="Vacancy Trend"
# #     )

# #     return fig


# # def create_vacancy_by_property_chart(data):

# #     if isinstance(data, dict) and "data" in data:
# #         data = data["data"]

# #     if not isinstance(data, list) or not data:
# #         return empty_chart("Vacancy by Property")

# #     properties = [x.get("property_name") for x in data]
# #     vacant = [x.get("vacant_units", 0) for x in data]

# #     fig = go.Figure(go.Bar(
# #         x=vacant,
# #         y=properties,
# #         orientation="h"
# #     ))

# #     fig.update_layout(
# #         paper_bgcolor="#0f172a",
# #         plot_bgcolor="#0f172a",
# #         font=dict(color="white"),
# #         height=420,
# #         title="Vacancy by Property"
# #     )

# #     return fig


# # def create_duration_bucket_chart(data):

# #     if isinstance(data, dict) and "data" in data:
# #         data = data["data"]

# #     if not isinstance(data, list) or not data:
# #         return empty_chart("Vacancy Duration Distribution")

# #     labels = [x.get("label") for x in data]
# #     values = [x.get("value", 0) for x in data]

# #     fig = go.Figure(go.Pie(
# #         labels=labels,
# #         values=values,
# #         hole=0.55,
# #         textinfo="percent",
# #         textposition="inside"
# #     ))

# #     fig.update_layout(
# #         paper_bgcolor="#0f172a",
# #         plot_bgcolor="#0f172a",
# #         font=dict(color="white"),
# #         height=420,
# #         title="Vacancy Duration Distribution"
# #     )

# #     return fig


# # def create_unit_type_chart(data):

# #     if isinstance(data, dict) and "data" in data:
# #         data = data["data"]

# #     if not isinstance(data, list) or not data:
# #         return empty_chart("Vacancy by Unit Type")

# #     unit_types = [x.get("unit_type") for x in data]
# #     vacant = [x.get("vacant", 0) for x in data]
# #     occupied = [x.get("occupied", 0) for x in data]

# #     fig = go.Figure()
# #     fig.add_bar(x=unit_types, y=occupied, name="Occupied")
# #     fig.add_bar(x=unit_types, y=vacant, name="Vacant")

# #     fig.update_layout(
# #         barmode="group",
# #         paper_bgcolor="#0f172a",
# #         plot_bgcolor="#0f172a",
# #         font=dict(color="white"),
# #         height=420,
# #         title="Vacancy by Unit Type"
# #     )

# #     return fig


# # # =====================================
# # # MAIN APP
# # # =====================================

# # def main():

# #     st.markdown(
# #         '<p class="main-header">📊 TERP Analytics Dashboard</p>',
# #         unsafe_allow_html=True
# #     )

# #     with st.sidebar:
# #         st.header("⚙️ Settings")
# #         auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)

# #         if st.button("🔄 Refresh Now"):
# #             st.cache_data.clear()
# #             st.rerun()

# #         st.markdown("---")
# #         st.markdown(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# #     leads = fetch_leads_dashboard()
# #     vacancy = fetch_vacancy_dashboard()

# #     if not leads or not vacancy:
# #         st.error("Unable to load dashboard data.")
# #         return

# #     lead_metrics = leads.get("metrics", {})
# #     vac_summary = vacancy.get("summary", {})

# #     # st.markdown('<p class="section-header">Executive Overview</p>', unsafe_allow_html=True)

# #     c1, c2, c3, c4, c5 = st.columns(5)

# #     c1.metric("Total Units", vac_summary.get("total_units", 0))
# #     c2.metric("Vacancy Rate", f"{vac_summary.get('vacancy_rate', 0):.1f}%")
# #     c3.metric("Active Leads", lead_metrics.get("total_leads", 0))
# #     # c4.metric("Conversion Rate", f"{lead_metrics.get('conversion_rate', 0):.1f}%")
# #     # c5.metric("Today's Leads", lead_metrics.get("todays_new_leads", 0))

# #     tab1, tab2 = st.tabs(["🏢 VACANCY", "🎯 LEADS"])

# #     with tab1:

# #         col1, col2 = st.columns(2)

# #         trend_data = vacancy.get("vacancy_trend")

# #         if trend_data:
# #             col1.plotly_chart(
# #                 create_vacancy_trend_chart(trend_data),
# #                 use_container_width=True
# #             )
# #         else:
# #             col1.plotly_chart(
# #                 create_duration_bucket_chart(
# #                     vacancy.get("vacancy_duration_buckets", [])
# #                 ),
# #                 use_container_width=True
# #             )

# #         col2.plotly_chart(
# #             create_vacancy_by_property_chart(
# #                 vacancy.get("vacancy_by_property", [])
# #             ),
# #             use_container_width=True
# #         )

# #         st.plotly_chart(
# #             create_unit_type_chart(
# #                 vacancy.get("vacancy_by_unit_type", [])
# #             ),
# #             use_container_width=True
# #         )

# #     with tab2:

# #         col1, col2 = st.columns(2)

# #         col1.plotly_chart(
# #             create_funnel_chart(
# #                 leads.get("conversion_funnel", {})
# #             ),
# #             use_container_width=True
# #         )

# #         col2.plotly_chart(
# #             create_ratings_chart(
# #                 leads.get("ratings_breakdown", [])
# #             ),
# #             use_container_width=True
# #         )

# #         st.markdown('<p class="section-header">Recent Lead Activity</p>', unsafe_allow_html=True)

# #         recent = fetch_recent_leads()

# #         if recent:
# #             df = pd.DataFrame(recent)
# #             st.dataframe(df, use_container_width=True, hide_index=True, height=400)
# #         else:
# #             st.info("No recent leads found.")

# #     if auto_refresh:
# #         time.sleep(30)
# #         st.rerun()


# # if __name__ == "__main__":
# #     main()


# ###########################
# """
# TERP Analytics Dashboard - Premium UI
# Tabs: VACANCY | REVENUE & RENT | LEADS

# Run:
#     streamlit run dashboardtrial.py
# """

# import streamlit as st
# import requests
# import plotly.graph_objects as go
# import pandas as pd
# from datetime import datetime
# import time

# # =====================================
# # CONFIG
# # =====================================

# API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# st.set_page_config(
#     page_title="TERP Analytics",
#     page_icon="📊",
#     layout="wide"
# )

# # =====================================
# # STYLING
# # =====================================

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

# html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

# .stApp {
#     background-color: #0a1120;
#     color: #e2e8f0;
# }

# section[data-testid="stSidebar"] {
#     background-color: #0a1120;
#     border-right: 1px solid rgba(148,163,184,0.08);
# }

# .stTabs [data-baseweb="tab-list"] {
#     gap: 4px;
#     background: #0d1829;
#     border-radius: 10px;
#     padding: 4px;
#     border: 1px solid rgba(148,163,184,0.08);
# }
# .stTabs [data-baseweb="tab"] {
#     border-radius: 8px;
#     padding: 8px 28px;
#     font-family: 'DM Sans', sans-serif;
#     font-weight: 600;
#     font-size: 0.83rem;
#     letter-spacing: 0.04em;
#     color: #94a3b8;
#     background: transparent;
#     border: none;
# }
# .stTabs [aria-selected="true"] {
#     background: #1e3a5f !important;
#     color: #38bdf8 !important;
# }

# [data-testid="stMetric"] {
#     background: linear-gradient(145deg, #0d1829, #111c2e);
#     padding: 18px 22px;
#     border-radius: 12px;
#     border: 1px solid rgba(148,163,184,0.08);
#     box-shadow: 0 4px 24px rgba(0,0,0,0.5);
# }
# [data-testid="stMetricLabel"] {
#     font-size: 0.72rem !important;
#     text-transform: uppercase;
#     letter-spacing: 0.08em;
#     color: #64748b !important;
# }
# [data-testid="stMetricValue"] {
#     font-family: 'Space Mono', monospace !important;
#     font-size: 1.5rem !important;
#     color: #e2e8f0 !important;
# }

# .main-header {
#     font-size: 2.2rem;
#     font-weight: 700;
#     background: linear-gradient(90deg, #38bdf8, #818cf8);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
#     margin-bottom: 1.2rem;
# }

# .section-header {
#     font-size: 1.3rem;
#     font-weight: 600;
#     margin-top: 2rem;
#     margin-bottom: 1rem;
#     padding-bottom: 0.4rem;
#     border-bottom: 1px solid rgba(148,163,184,0.2);
# }

# .rev-kpi-card {
#     background: linear-gradient(145deg, #0d1829, #111c2e);
#     border-radius: 12px;
#     border: 1px solid rgba(148,163,184,0.08);
#     padding: 16px 20px 14px;
#     box-shadow: 0 4px 24px rgba(0,0,0,0.5);
#     margin-bottom: 4px;
#     min-height: 100px;
# }
# .rev-kpi-label {
#     font-size: 0.68rem;
#     text-transform: uppercase;
#     letter-spacing: 0.1em;
#     color: #64748b;
#     margin-bottom: 6px;
# }
# .rev-kpi-value {
#     font-family: 'Space Mono', monospace;
#     font-size: 1.7rem;
#     font-weight: 700;
#     line-height: 1.15;
# }
# .rev-kpi-delta { font-size: 0.74rem; margin-top: 4px; color: #64748b; }

# .badge {
#     display: inline-block;
#     font-size: 0.58rem;
#     font-weight: 700;
#     letter-spacing: 0.07em;
#     text-transform: uppercase;
#     padding: 2px 7px;
#     border-radius: 20px;
#     float: right;
#     margin-top: 2px;
# }
# .badge-red    { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
# .badge-green  { background: rgba(52,211,153,0.1);  color: #34d399; border: 1px solid rgba(52,211,153,0.22); }
# .badge-yellow { background: rgba(251,191,36,0.1);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.22); }
# .badge-blue   { background: rgba(56,189,248,0.1);  color: #38bdf8; border: 1px solid rgba(56,189,248,0.22); }
# .badge-purple { background: rgba(167,139,250,0.1); color: #a78bfa; border: 1px solid rgba(167,139,250,0.22); }

# .color-red    { color: #f87171; }
# .color-green  { color: #34d399; }
# .color-yellow { color: #fbbf24; }
# .color-blue   { color: #38bdf8; }
# .color-purple { color: #a78bfa; }

# .section-label {
#     font-size: 0.7rem;
#     font-weight: 700;
#     letter-spacing: 0.1em;
#     text-transform: uppercase;
#     color: #475569;
#     margin: 1.2rem 0 0.5rem;
#     padding-bottom: 0.35rem;
#     border-bottom: 1px solid rgba(148,163,184,0.07);
# }
# </style>
# """, unsafe_allow_html=True)

# # =====================================
# # CHART THEME
# # =====================================

# DARK_BG = "#0a1120"

# CHART_THEME = dict(
#     paper_bgcolor=DARK_BG,
#     plot_bgcolor=DARK_BG,
#     font=dict(family="DM Sans", color="#94a3b8", size=12),
#     margin=dict(l=10, r=10, t=40, b=10),
#     legend=dict(
#         bgcolor="rgba(0,0,0,0)",
#         bordercolor="rgba(0,0,0,0)",
#         font=dict(size=11),
#     ),
# )


# def empty_chart(title="No data", height=420):
#     fig = go.Figure()
#     fig.update_layout(height=height, title=title, **CHART_THEME)
#     return fig


# def fmt_inr(val):
#     if val is None:
#         return "—"
#     val = float(val)
#     if abs(val) >= 1e7:
#         return f"₹{val/1e7:.2f}Cr"
#     if abs(val) >= 1e5:
#         return f"₹{val/1e5:.1f}L"
#     return f"₹{val:,.0f}"


# # =====================================
# # API CALLS
# # =====================================

# @st.cache_data(ttl=30)
# def fetch_leads_dashboard():
#     try:
#         r = requests.get(f"{API_BASE_URL}/leads-dashboard/", timeout=10)
#         r.raise_for_status()
#         return r.json()
#     except Exception as e:
#         st.error(f"Leads API Error: {e}")
#         return None


# @st.cache_data(ttl=30)
# def fetch_vacancy_dashboard():
#     try:
#         r = requests.get(f"{API_BASE_URL}/vacancy-dashboard/", timeout=10)
#         r.raise_for_status()
#         return r.json()
#     except Exception as e:
#         st.error(f"Vacancy API Error: {e}")
#         return None


# @st.cache_data(ttl=15)
# def fetch_recent_leads(limit=20):
#     try:
#         r = requests.get(
#             f"{API_BASE_URL}/leads-dashboard/live/recent",
#             params={"limit": limit},
#             timeout=10
#         )
#         r.raise_for_status()
#         return r.json().get("recent_leads", [])
#     except Exception:
#         return []


# @st.cache_data(ttl=30)
# def fetch_revenue_dashboard():
#     try:
#         r = requests.get(f"{API_BASE_URL}/revenue-dashboard/", timeout=20)
#         r.raise_for_status()
#         return r.json()
#     except Exception as e:
#         st.error(f"Revenue API Error: {e}")
#         return None


# # =====================================
# # LEADS CHARTS
# # =====================================

# def create_funnel_chart(data):
#     if not data:
#         return empty_chart("Lead Conversion Funnel")

#     mapping = [
#         ("New Lead",    data.get("New Lead", 0)),
#         ("Prospect",    data.get("Prospect", 0)),
#         ("Opportunity", data.get("Opportunity", 0)),
#         ("Converted",   data.get("Convert to Tenant", 0)),
#     ]
#     filtered = [(s, v) for s, v in mapping if v > 0]
#     if not filtered:
#         return empty_chart("Lead Conversion Funnel")

#     fig = go.Figure(go.Funnel(
#         y=[x[0] for x in filtered],
#         x=[x[1] for x in filtered],
#         textinfo="value+percent total",
#         marker_color=["#38bdf8", "#818cf8", "#a78bfa", "#34d399"],
#     ))
#     fig.update_layout(height=420, title="Lead Conversion Funnel", **CHART_THEME)
#     return fig


# def create_ratings_chart(data):
#     if not data:
#         return empty_chart("Lead Ratings Distribution")

#     labels = [r.get("rating", "Unknown") for r in data]
#     values = [r.get("lead_count", 0) for r in data]

#     fig = go.Figure(go.Pie(
#         labels=labels,
#         values=values,
#         hole=0.55,
#         textinfo="percent+label",
#     ))
#     fig.update_layout(height=420, title="Lead Ratings Distribution", **CHART_THEME)
#     return fig


# # =====================================
# # VACANCY CHARTS
# # =====================================

# def create_vacancy_trend_chart(data):
#     if isinstance(data, dict) and "data" in data:
#         data = data["data"]
#     if not isinstance(data, list) or not data:
#         return empty_chart("Vacancy Rate Trend")

#     months   = [x.get("month") for x in data]
#     occupied = [x.get("occupied_units", 0) for x in data]
#     vacant   = [x.get("vacant_units", 0) for x in data]

#     fig = go.Figure()
#     fig.add_bar(x=months, y=occupied, name="Occupied", marker_color="#10b981")
#     fig.add_bar(x=months, y=vacant,   name="Vacant",   marker_color="#ef4444")
#     fig.update_layout(barmode="stack", height=420, title="Vacancy Trend", **CHART_THEME)
#     return fig


# def create_vacancy_by_property_chart(data):
#     if isinstance(data, dict) and "data" in data:
#         data = data["data"]
#     if not isinstance(data, list) or not data:
#         return empty_chart("Vacancy by Property")

#     properties = [x.get("property_name") for x in data]
#     vacant     = [x.get("vacant_units", 0) for x in data]

#     fig = go.Figure(go.Bar(
#         x=vacant, y=properties, orientation="h",
#         marker_color="#38bdf8",
#     ))
#     fig.update_layout(height=420, title="Vacancy by Property", **CHART_THEME)
#     return fig


# def create_duration_bucket_chart(data):
#     if isinstance(data, dict) and "data" in data:
#         data = data["data"]
#     if not isinstance(data, list) or not data:
#         return empty_chart("Vacancy Duration Distribution")

#     labels = [x.get("label") for x in data]
#     values = [x.get("value", 0) for x in data]
#     colors = ["#10b981", "#f59e0b", "#f97316", "#ef4444"]

#     fig = go.Figure(go.Pie(
#         labels=labels, values=values, hole=0.55,
#         textinfo="percent", textposition="inside",
#         marker=dict(colors=colors),
#     ))
#     fig.update_layout(height=420, title="Vacancy Duration Distribution", **CHART_THEME)
#     return fig


# def create_unit_type_chart(data):
#     if isinstance(data, dict) and "data" in data:
#         data = data["data"]
#     if not isinstance(data, list) or not data:
#         return empty_chart("Vacancy by Unit Type")

#     unit_types = [x.get("unit_type") for x in data]
#     vacant     = [x.get("vacant", 0) for x in data]
#     occupied   = [x.get("occupied", 0) for x in data]

#     fig = go.Figure()
#     fig.add_bar(x=unit_types, y=occupied, name="Occupied", marker_color="#10b981")
#     fig.add_bar(x=unit_types, y=vacant,   name="Vacant",   marker_color="#ef4444")
#     fig.update_layout(barmode="group", height=420, title="Vacancy by Unit Type", **CHART_THEME)
#     return fig


# # =====================================
# # REVENUE CHARTS
# # =====================================

# def create_rental_loss_breakdown_donut(data):
#     if not data:
#         return empty_chart("Rental Loss Breakdown")

#     labels = [d["cause"] for d in data]
#     values = [d["value"] for d in data]
#     colors = [d.get("color", "#94a3b8") for d in data]

#     fig = go.Figure(go.Pie(
#         labels=labels,
#         values=values,
#         hole=0.62,
#         textinfo="percent",
#         textposition="inside",
#         marker=dict(colors=colors, line=dict(color=DARK_BG, width=2)),
#     ))
#     fig.update_layout(
#         height=400,
#         title=dict(text="Rental Loss Breakdown", font=dict(size=14)),
#         annotations=[dict(
#             text="By cause", x=0.5, y=0.5,
#             font=dict(size=11, color="#64748b"), showarrow=False,
#         )],
#         **CHART_THEME,
#     )
#     return fig


# def create_rental_loss_trend(data):
#     if not data:
#         return empty_chart("Rental Loss Trend")

#     months    = [d["rent_month"] for d in data]
#     expected  = [d["expected"]  / 1e5 for d in data]
#     collected = [d["collected"] / 1e5 for d in data]
#     loss      = [d["loss"]      / 1e5 for d in data]

#     fig = go.Figure()
#     fig.add_scatter(
#         x=months, y=expected, mode="lines+markers", name="Potential Revenue",
#         line=dict(color="#06b6d4", width=2, dash="dot"), marker=dict(size=5),
#     )
#     fig.add_scatter(
#         x=months, y=collected, mode="lines+markers", name="Actual Revenue",
#         line=dict(color="#34d399", width=2), marker=dict(size=5),
#     )
#     fig.add_scatter(
#         x=months, y=loss, mode="lines+markers", name="Loss",
#         line=dict(color="#f87171", width=2), marker=dict(size=5),
#         fill="tozeroy", fillcolor="rgba(248,113,113,0.06)",
#     )
#     fig.update_layout(
#         height=400,
#         title=dict(text="Rental Loss Trend  (₹ Lakhs)", font=dict(size=14)),
#         yaxis=dict(title="₹ Lakhs"),
#         **CHART_THEME,
#     )
#     return fig


# def create_income_expense_trend(data):
#     if not data:
#         return empty_chart("Income vs Expense")

#     months  = [d["month"] for d in data]
#     income  = [d["income"]  / 1e5 for d in data]
#     expense = [d["expense"] / 1e5 for d in data]
#     net     = [d["net"]     / 1e5 for d in data]

#     fig = go.Figure()
#     fig.add_bar(x=months, y=income,  name="Income",  marker_color="#34d399")
#     fig.add_bar(x=months, y=expense, name="Expense", marker_color="#f87171")
#     fig.add_scatter(
#         x=months, y=net, name="Net",
#         mode="lines+markers", line=dict(color="#fbbf24", width=2),
#     )
#     fig.update_layout(
#         barmode="group",
#         height=400,
#         title=dict(text="Income vs Expense  (₹ Lakhs)", font=dict(size=14)),
#         **CHART_THEME,
#     )
#     return fig


# def create_loss_by_property_chart(data):
#     if not data:
#         return empty_chart("Rental Loss by Property")

#     top       = data[:10]
#     props     = [d["property_name"] for d in top]
#     collected = [d["collected"] / 1e5 for d in top]
#     loss      = [d["loss"]      / 1e5 for d in top]

#     fig = go.Figure()
#     fig.add_bar(x=collected, y=props, orientation="h", name="Collected", marker_color="#34d399")
#     fig.add_bar(x=loss,      y=props, orientation="h", name="Loss",      marker_color="#ef4444")
#     fig.update_layout(
#         barmode="stack",
#         height=420,
#         title=dict(text="Collected vs Loss by Property  (₹ Lakhs)", font=dict(size=14)),
#         **CHART_THEME,
#     )
#     return fig


# def create_collection_rate_gauge(rate: float):
#     fig = go.Figure(go.Indicator(
#         mode="gauge+number+delta",
#         value=rate,
#         number=dict(suffix="%", font=dict(size=34, family="Space Mono", color="#e2e8f0")),
#         delta=dict(
#             reference=90,
#             increasing=dict(color="#34d399"),
#             decreasing=dict(color="#f87171"),
#         ),
#         gauge=dict(
#             axis=dict(range=[0, 100], tickcolor="#475569"),
#             bar=dict(color="#38bdf8"),
#             bgcolor=DARK_BG,
#             bordercolor="#1e293b",
#             steps=[
#                 dict(range=[0, 60],   color="#1c1c2e"),
#                 dict(range=[60, 80],  color="#1a2535"),
#                 dict(range=[80, 100], color="#162033"),
#             ],
#             threshold=dict(
#                 line=dict(color="#fbbf24", width=3),
#                 thickness=0.75, value=90,
#             ),
#         ),
#         title=dict(text="Collection Rate", font=dict(size=13, color="#64748b")),
#     ))
#     fig.update_layout(
#         height=260,
#         paper_bgcolor=DARK_BG,
#         font=dict(color="#94a3b8"),
#         margin=dict(l=30, r=30, t=40, b=10),
#     )
#     return fig


# # =====================================
# # REVENUE KPI CARD HTML
# # =====================================

# def rev_kpi(label, value_str, delta_str, color_cls, badge_text, badge_cls):
#     return f"""
# <div class="rev-kpi-card">
#   <div class="rev-kpi-label">
#     {label}
#     <span class="badge {badge_cls}">{badge_text}</span>
#   </div>
#   <div class="rev-kpi-value {color_cls}">{value_str}</div>
#   <div class="rev-kpi-delta">{delta_str}</div>
# </div>
# """


# # =====================================
# # REVENUE TAB RENDERER
# # =====================================

# def render_revenue_tab(rev):
#     kpis            = rev.get("kpis", {})
#     total_loss      = kpis.get("total_loss", 0)
#     total_expected  = kpis.get("total_expected", 0)
#     total_collected = kpis.get("total_collected", 0)
#     collection_rate = kpis.get("collection_rate", 0)
#     loss_change     = kpis.get("loss_change_vs_prev", 0)
#     rate_change     = kpis.get("rate_change_vs_prev", 0)
#     annual_loss     = total_loss * 12
#     num_properties  = len(rev.get("rental_loss_by_property", []))

#     # ── KPI row ──────────────────────────────────────────────
#     c1, c2, c3, c4, c5 = st.columns(5)

#     with c1:
#         st.markdown(rev_kpi(
#             "Total Rental Loss / Mo",
#             fmt_inr(total_loss),
#             f"{'▲' if loss_change > 0 else '▼'} {fmt_inr(abs(loss_change))} vs prev",
#             "color-red", "Revenue leak", "badge-red",
#         ), unsafe_allow_html=True)

#     with c2:
#         st.markdown(rev_kpi(
#             "Properties w/ Loss",
#             str(num_properties),
#             "Requires attention",
#             "color-yellow", "Action needed", "badge-yellow",
#         ), unsafe_allow_html=True)

#     with c3:
#         st.markdown(rev_kpi(
#             "Collection Rate",
#             f"{collection_rate:.1f}%",
#             f"{'▲' if rate_change >= 0 else '▼'} {abs(rate_change):.1f}% MoM",
#             "color-green", "MoM tracking", "badge-green",
#         ), unsafe_allow_html=True)

#     with c4:
#         st.markdown(rev_kpi(
#             "Projected Loss (12M)",
#             fmt_inr(annual_loss),
#             "if trend holds",
#             "color-purple", "Projection", "badge-purple",
#         ), unsafe_allow_html=True)

#     with c5:
#         st.markdown(rev_kpi(
#             "Total Expected Rent",
#             fmt_inr(total_expected),
#             f"Collected: {fmt_inr(total_collected)}",
#             "color-blue", "Current month", "badge-blue",
#         ), unsafe_allow_html=True)

#     # ── Loss Analysis ─────────────────────────────────────────
#     st.markdown('<div class="section-label">Loss Analysis</div>', unsafe_allow_html=True)

#     col1, col2 = st.columns([3, 2])

#     with col1:
#         st.plotly_chart(
#             create_rental_loss_breakdown_donut(rev.get("rental_loss_breakdown", [])),
#             use_container_width=True,
#         )

#     with col2:
#         st.plotly_chart(
#             create_collection_rate_gauge(collection_rate),
#             use_container_width=True,
#         )
#         st.markdown('<div class="section-label">Loss by Unit Type</div>', unsafe_allow_html=True)
#         unit_data = rev.get("rental_loss_by_unit_type", [])
#         if unit_data:
#             udf = pd.DataFrame(unit_data)[
#                 ["unit_type", "expected", "collected", "loss", "collection_rate"]
#             ]
#             udf.columns = ["Unit Type", "Expected", "Collected", "Loss", "Rate %"]
#             udf["Expected"]  = udf["Expected"].apply(fmt_inr)
#             udf["Collected"] = udf["Collected"].apply(fmt_inr)
#             udf["Loss"]      = udf["Loss"].apply(fmt_inr)
#             st.dataframe(udf, use_container_width=True, hide_index=True, height=190)
#         else:
#             st.info("No unit type data.")

#     # ── Trends ────────────────────────────────────────────────
#     st.markdown('<div class="section-label">Trends</div>', unsafe_allow_html=True)

#     col3, col4 = st.columns(2)
#     with col3:
#         st.plotly_chart(
#             create_rental_loss_trend(rev.get("monthly_rent_trend", [])),
#             use_container_width=True,
#         )
#     with col4:
#         st.plotly_chart(
#             create_income_expense_trend(rev.get("income_expense_trend", [])),
#             use_container_width=True,
#         )

#     # ── Property Breakdown ───────────────────────────────────
#     st.markdown('<div class="section-label">Property Breakdown</div>', unsafe_allow_html=True)
#     st.plotly_chart(
#         create_loss_by_property_chart(rev.get("rental_loss_by_property", [])),
#         use_container_width=True,
#     )


# # =====================================
# # MAIN APP
# # =====================================

# def main():
#     st.markdown(
#         '<p class="main-header">📊 TERP Analytics Dashboard</p>',
#         unsafe_allow_html=True
#     )

#     with st.sidebar:
#         st.header("⚙️ Settings")
#         auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)

#         if st.button("🔄 Refresh Now"):
#             st.cache_data.clear()
#             st.rerun()

#         st.markdown("---")
#         st.markdown(f"Last Updated: `{datetime.now().strftime('%H:%M:%S')}`")

#     # ── Fetch all data ─────────────────────────────────────────
#     leads   = fetch_leads_dashboard()
#     vacancy = fetch_vacancy_dashboard()
#     revenue = fetch_revenue_dashboard()

#     # ── Executive KPI strip ───────────────────────────────────
#     lead_metrics = (leads   or {}).get("metrics", {})
#     vac_summary  = (vacancy or {}).get("summary", {})
#     rev_kpis     = (revenue or {}).get("kpis", {})

#     c1, c2, c3, c4, c5 = st.columns(5)
#     c1.metric("Total Units",     vac_summary.get("total_units", "—"))
#     c2.metric("Vacancy Rate",    f"{vac_summary.get('vacancy_rate', 0):.1f}%")
#     c3.metric("Active Leads",    lead_metrics.get("total_leads", "—"))
#     c4.metric("Collection Rate", f"{rev_kpis.get('collection_rate', 0):.1f}%")
#     c5.metric("Monthly Loss",    fmt_inr(rev_kpis.get("total_loss", 0)))

#     # ── Tabs ──────────────────────────────────────────────────
#     tab_vac, tab_rev, tab_leads = st.tabs([
#         "🏢  VACANCY",
#         "💰  REVENUE & RENT",
#         "🎯  LEADS",
#     ])

#     # ── VACANCY TAB ───────────────────────────────────────────
#     with tab_vac:
#         if not vacancy:
#             st.error("Unable to load vacancy data.")
#         else:
#             col1, col2 = st.columns(2)

#             trend_data = vacancy.get("vacancy_trend")
#             if trend_data:
#                 col1.plotly_chart(
#                     create_vacancy_trend_chart(trend_data),
#                     use_container_width=True,
#                 )
#             else:
#                 col1.plotly_chart(
#                     create_duration_bucket_chart(
#                         vacancy.get("vacancy_duration_buckets", [])
#                     ),
#                     use_container_width=True,
#                 )

#             col2.plotly_chart(
#                 create_vacancy_by_property_chart(
#                     vacancy.get("vacancy_by_property", [])
#                 ),
#                 use_container_width=True,
#             )

#             st.plotly_chart(
#                 create_unit_type_chart(
#                     vacancy.get("vacancy_by_unit_type", [])
#                 ),
#                 use_container_width=True,
#             )

#     # ── REVENUE & RENT TAB ────────────────────────────────────
#     with tab_rev:
#         if not revenue:
#             st.error("Unable to load revenue data.")
#             st.info(
#                 "Register the router in `app/api/v1/api.py`:\n\n"
#                 "```python\n"
#                 "from app.api.v1.endpoints import revenue_dashboard\n"
#                 "api_router.include_router(\n"
#                 "    revenue_dashboard.router,\n"
#                 "    prefix='/revenue-dashboard',\n"
#                 "    tags=['Revenue Dashboard']\n"
#                 ")\n```"
#             )
#         else:
#             render_revenue_tab(revenue)

#     # ── LEADS TAB ─────────────────────────────────────────────
#     with tab_leads:
#         if not leads:
#             st.error("Unable to load leads data.")
#         else:
#             col1, col2 = st.columns(2)

#             col1.plotly_chart(
#                 create_funnel_chart(leads.get("conversion_funnel", {})),
#                 use_container_width=True,
#             )
#             col2.plotly_chart(
#                 create_ratings_chart(leads.get("ratings_breakdown", [])),
#                 use_container_width=True,
#             )

#             st.markdown(
#                 '<p class="section-header">Recent Lead Activity</p>',
#                 unsafe_allow_html=True,
#             )

#             recent = fetch_recent_leads()
#             if recent:
#                 df = pd.DataFrame(recent)
#                 st.dataframe(df, use_container_width=True, hide_index=True, height=400)
#             else:
#                 st.info("No recent leads found.")

#     if auto_refresh:
#         time.sleep(30)
#         st.rerun()


# if __name__ == "__main__":
#     main()
######################################new#######################
"""
TERP Analytics Dashboard - Premium UI
Tabs: VACANCY | REVENUE & RENT | LEADS

Run:
    streamlit run dashboardtrial.py
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import time

# =====================================
# CONFIG
# =====================================

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="TERP Analytics",
    page_icon="📊",
    layout="wide"
)

# =====================================
# STYLING
# =====================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp {
    background-color: #0a1120;
    color: #e2e8f0;
}

section[data-testid="stSidebar"] {
    background-color: #0a1120;
    border-right: 1px solid rgba(148,163,184,0.08);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #0d1829;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(148,163,184,0.08);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 28px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.83rem;
    letter-spacing: 0.04em;
    color: #94a3b8;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #38bdf8 !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #0d1829, #111c2e);
    padding: 18px 22px;
    border-radius: 12px;
    border: 1px solid rgba(148,163,184,0.08);
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 1.5rem !important;
    color: #e2e8f0 !important;
}

.main-header {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.2rem;
}

.section-header {
    font-size: 1.3rem;
    font-weight: 600;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(148,163,184,0.2);
}

.rev-kpi-card {
    background: linear-gradient(145deg, #0d1829, #111c2e);
    border-radius: 12px;
    border: 1px solid rgba(148,163,184,0.08);
    padding: 16px 20px 14px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
    margin-bottom: 4px;
    min-height: 100px;
}
.rev-kpi-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    margin-bottom: 6px;
}
.rev-kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.7rem;
    font-weight: 700;
    line-height: 1.15;
}
.rev-kpi-delta { font-size: 0.74rem; margin-top: 4px; color: #64748b; }

.badge {
    display: inline-block;
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 20px;
    float: right;
    margin-top: 2px;
}
.badge-red    { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.badge-green  { background: rgba(52,211,153,0.1);  color: #34d399; border: 1px solid rgba(52,211,153,0.22); }
.badge-yellow { background: rgba(251,191,36,0.1);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.22); }
.badge-blue   { background: rgba(56,189,248,0.1);  color: #38bdf8; border: 1px solid rgba(56,189,248,0.22); }
.badge-purple { background: rgba(167,139,250,0.1); color: #a78bfa; border: 1px solid rgba(167,139,250,0.22); }

.color-red    { color: #f87171; }
.color-green  { color: #34d399; }
.color-yellow { color: #fbbf24; }
.color-blue   { color: #38bdf8; }
.color-purple { color: #a78bfa; }

.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    margin: 1.2rem 0 0.5rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid rgba(148,163,184,0.07);
}

/* Funnel rate pill */
.funnel-pill {
    background: linear-gradient(135deg, #0d1829, #111c2e);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.funnel-pill-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    margin-bottom: 6px;
}
.funnel-pill-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
}
.funnel-pill-sub {
    font-size: 0.7rem;
    color: #64748b;
    margin-top: 4px;
}

/* Verdict badge */
.verdict-card {
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 8px;
    border: 1px solid rgba(148,163,184,0.1);
}
.verdict-no-leads    { background: rgba(239,68,68,0.08);  border-color: rgba(239,68,68,0.2); }
.verdict-insufficient{ background: rgba(251,191,36,0.08); border-color: rgba(251,191,36,0.2); }
.verdict-sufficient  { background: rgba(56,189,248,0.08); border-color: rgba(56,189,248,0.2); }
.verdict-well-covered{ background: rgba(52,211,153,0.08); border-color: rgba(52,211,153,0.2); }
</style>
""", unsafe_allow_html=True)

# =====================================
# CHART THEME
# =====================================

DARK_BG = "#0a1120"

CHART_THEME = dict(
    paper_bgcolor=DARK_BG,
    plot_bgcolor=DARK_BG,
    font=dict(family="DM Sans", color="#94a3b8", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
        font=dict(size=11),
    ),
)


def empty_chart(title="No data", height=420):
    fig = go.Figure()
    fig.update_layout(height=height, title=title, **CHART_THEME)
    return fig


def fmt_inr(val):
    if val is None:
        return "—"
    val = float(val)
    if abs(val) >= 1e7:
        return f"₹{val/1e7:.2f}Cr"
    if abs(val) >= 1e5:
        return f"₹{val/1e5:.1f}L"
    return f"₹{val:,.0f}"


# =====================================
# API CALLS
# =====================================

@st.cache_data(ttl=30)
def fetch_leads_dashboard():
    try:
        r = requests.get(f"{API_BASE_URL}/leads-dashboard/", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Leads API Error: {e}")
        return None


@st.cache_data(ttl=30)
def fetch_vacancy_dashboard():
    try:
        r = requests.get(f"{API_BASE_URL}/vacancy-dashboard/", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Vacancy API Error: {e}")
        return None


@st.cache_data(ttl=15)
def fetch_recent_leads(limit=20):
    try:
        r = requests.get(
            f"{API_BASE_URL}/leads-dashboard/live/recent",
            params={"limit": limit},
            timeout=10
        )
        r.raise_for_status()
        return r.json().get("recent_leads", [])
    except Exception:
        return []


@st.cache_data(ttl=30)
def fetch_revenue_dashboard():
    try:
        r = requests.get(f"{API_BASE_URL}/revenue-dashboard/", timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Revenue API Error: {e}")
        return None


# =====================================
# LEADS CHARTS
# =====================================

def create_funnel_chart(data):
    if not data:
        return empty_chart("Lead Conversion Funnel")

    mapping = [
        ("New Lead",    data.get("New Lead", 0)),
        ("Prospect",    data.get("Prospect", 0)),
        ("Opportunity", data.get("Opportunity", 0)),
        ("Converted",   data.get("Convert to Tenant", 0)),
    ]
    filtered = [(s, v) for s, v in mapping if v > 0]
    if not filtered:
        return empty_chart("Lead Conversion Funnel")

    fig = go.Figure(go.Funnel(
        y=[x[0] for x in filtered],
        x=[x[1] for x in filtered],
        textinfo="value+percent total",
        marker_color=["#38bdf8", "#818cf8", "#a78bfa", "#34d399"],
    ))
    fig.update_layout(height=380, title="Lead Conversion Funnel", **CHART_THEME)
    return fig


def create_ratings_chart(data):
    if not data:
        return empty_chart("Lead Ratings Distribution")

    labels = [r.get("rating", "Unknown") for r in data]
    values = [r.get("lead_count", 0) for r in data]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        textinfo="percent+label",
        marker=dict(colors=["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f87171"]),
    ))
    fig.update_layout(height=380, title="Lead Ratings Distribution", **CHART_THEME)
    return fig


def create_vacant_coverage_gauge(pct: float, verdict: str):
    color = {
        "No Leads at All": "#ef4444",
        "Insufficient":    "#f59e0b",
        "Sufficient":      "#38bdf8",
        "Well Covered":    "#34d399",
    }.get(verdict, "#94a3b8")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number=dict(suffix="%", font=dict(size=30, family="Space Mono", color="#e2e8f0")),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#475569"),
            bar=dict(color=color),
            bgcolor=DARK_BG,
            bordercolor="#1e293b",
            steps=[
                dict(range=[0,  40], color="#1c1c2e"),
                dict(range=[40, 70], color="#1a2535"),
                dict(range=[70, 100], color="#162033"),
            ],
        ),
        title=dict(text="Units Covered by Leads", font=dict(size=12, color="#64748b")),
    ))
    fig.update_layout(
        height=240,
        paper_bgcolor=DARK_BG,
        font=dict(color="#94a3b8"),
        margin=dict(l=30, r=30, t=40, b=10),
    )
    return fig


def create_low_conversion_chart(units: list):
    if not units:
        return None

    unit_labels = [f"{u['unit_code']}\n{u['property_name']}" for u in units]
    rates       = [u["conversion_rate_pct"] for u in units]
    colors      = ["#ef4444" if u["conversion_flag"] == "Low Conversion" else "#34d399" for u in units]

    fig = go.Figure(go.Bar(
        x=rates,
        y=unit_labels,
        orientation="h",
        marker_color=colors,
        text=[f"{r:.1f}%" for r in rates],
        textposition="outside",
    ))
    fig.update_layout(
        height=max(300, len(units) * 40),
        title="Hot-Lead Units — Conversion Rate",
        xaxis=dict(title="Conversion %", range=[0, 110]),
        **CHART_THEME,
    )
    return fig


# =====================================
# VACANCY CHARTS
# =====================================

def create_vacancy_trend_chart(data):
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if not isinstance(data, list) or not data:
        return empty_chart("Vacancy Rate Trend")

    months   = [x.get("month") for x in data]
    occupied = [x.get("occupied_units", 0) for x in data]
    vacant   = [x.get("vacant_units", 0) for x in data]

    fig = go.Figure()
    fig.add_bar(x=months, y=occupied, name="Occupied", marker_color="#10b981")
    fig.add_bar(x=months, y=vacant,   name="Vacant",   marker_color="#ef4444")
    fig.update_layout(barmode="stack", height=420, title="Vacancy Trend", **CHART_THEME)
    return fig


def create_vacancy_by_property_chart(data):
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if not isinstance(data, list) or not data:
        return empty_chart("Vacancy by Property")

    properties = [x.get("property_name") for x in data]
    vacant     = [x.get("vacant_units", 0) for x in data]

    fig = go.Figure(go.Bar(
        x=vacant, y=properties, orientation="h",
        marker_color="#38bdf8",
    ))
    fig.update_layout(height=420, title="Vacancy by Property", **CHART_THEME)
    return fig


def create_duration_bucket_chart(data):
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if not isinstance(data, list) or not data:
        return empty_chart("Vacancy Duration Distribution")

    labels = [x.get("label") for x in data]
    values = [x.get("value", 0) for x in data]
    colors = ["#10b981", "#f59e0b", "#f97316", "#ef4444"]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        textinfo="percent", textposition="inside",
        marker=dict(colors=colors),
    ))
    fig.update_layout(height=420, title="Vacancy Duration Distribution", **CHART_THEME)
    return fig


def create_unit_type_chart(data):
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if not isinstance(data, list) or not data:
        return empty_chart("Vacancy by Unit Type")

    unit_types = [x.get("unit_type") for x in data]
    vacant     = [x.get("vacant", 0) for x in data]
    occupied   = [x.get("occupied", 0) for x in data]

    fig = go.Figure()
    fig.add_bar(x=unit_types, y=occupied, name="Occupied", marker_color="#10b981")
    fig.add_bar(x=unit_types, y=vacant,   name="Vacant",   marker_color="#ef4444")
    fig.update_layout(barmode="group", height=420, title="Vacancy by Unit Type", **CHART_THEME)
    return fig


# =====================================
# REVENUE CHARTS
# =====================================

def create_rental_loss_breakdown_donut(data):
    if not data:
        return empty_chart("Rental Loss Breakdown")

    labels = [d["cause"] for d in data]
    values = [d["value"] for d in data]
    colors = [d.get("color", "#94a3b8") for d in data]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        textinfo="percent", textposition="inside",
        marker=dict(colors=colors, line=dict(color=DARK_BG, width=2)),
    ))
    fig.update_layout(
        height=400,
        title=dict(text="Rental Loss Breakdown", font=dict(size=14)),
        annotations=[dict(
            text="By cause", x=0.5, y=0.5,
            font=dict(size=11, color="#64748b"), showarrow=False,
        )],
        **CHART_THEME,
    )
    return fig


def create_rental_loss_trend(data):
    if not data:
        return empty_chart("Rental Loss Trend")

    months    = [d["rent_month"] for d in data]
    expected  = [d["expected"]  / 1e5 for d in data]
    collected = [d["collected"] / 1e5 for d in data]
    loss      = [d["loss"]      / 1e5 for d in data]

    fig = go.Figure()
    fig.add_scatter(x=months, y=expected,  mode="lines+markers", name="Potential Revenue",
                    line=dict(color="#06b6d4", width=2, dash="dot"), marker=dict(size=5))
    fig.add_scatter(x=months, y=collected, mode="lines+markers", name="Actual Revenue",
                    line=dict(color="#34d399", width=2), marker=dict(size=5))
    fig.add_scatter(x=months, y=loss,      mode="lines+markers", name="Loss",
                    line=dict(color="#f87171", width=2), marker=dict(size=5),
                    fill="tozeroy", fillcolor="rgba(248,113,113,0.06)")
    fig.update_layout(height=400, title=dict(text="Rental Loss Trend  (₹ Lakhs)", font=dict(size=14)),
                      yaxis=dict(title="₹ Lakhs"), **CHART_THEME)
    return fig


def create_income_expense_trend(data):
    if not data:
        return empty_chart("Income vs Expense")

    months  = [d["month"] for d in data]
    income  = [d["income"]  / 1e5 for d in data]
    expense = [d["expense"] / 1e5 for d in data]
    net     = [d["net"]     / 1e5 for d in data]

    fig = go.Figure()
    fig.add_bar(x=months, y=income,  name="Income",  marker_color="#34d399")
    fig.add_bar(x=months, y=expense, name="Expense", marker_color="#f87171")
    fig.add_scatter(x=months, y=net, name="Net",
                    mode="lines+markers", line=dict(color="#fbbf24", width=2))
    fig.update_layout(barmode="group", height=400,
                      title=dict(text="Income vs Expense  (₹ Lakhs)", font=dict(size=14)),
                      **CHART_THEME)
    return fig


def create_loss_by_property_chart(data):
    if not data:
        return empty_chart("Rental Loss by Property")

    top       = data[:10]
    props     = [d["property_name"] for d in top]
    collected = [d["collected"] / 1e5 for d in top]
    loss      = [d["loss"]      / 1e5 for d in top]

    fig = go.Figure()
    fig.add_bar(x=collected, y=props, orientation="h", name="Collected", marker_color="#34d399")
    fig.add_bar(x=loss,      y=props, orientation="h", name="Loss",      marker_color="#ef4444")
    fig.update_layout(barmode="stack", height=420,
                      title=dict(text="Collected vs Loss by Property  (₹ Lakhs)", font=dict(size=14)),
                      **CHART_THEME)
    return fig


def create_collection_rate_gauge(rate: float):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rate,
        number=dict(suffix="%", font=dict(size=34, family="Space Mono", color="#e2e8f0")),
        delta=dict(reference=90, increasing=dict(color="#34d399"), decreasing=dict(color="#f87171")),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#475569"),
            bar=dict(color="#38bdf8"),
            bgcolor=DARK_BG,
            bordercolor="#1e293b",
            steps=[
                dict(range=[0,  60], color="#1c1c2e"),
                dict(range=[60, 80], color="#1a2535"),
                dict(range=[80, 100], color="#162033"),
            ],
            threshold=dict(line=dict(color="#fbbf24", width=3), thickness=0.75, value=90),
        ),
        title=dict(text="Collection Rate", font=dict(size=13, color="#64748b")),
    ))
    fig.update_layout(height=260, paper_bgcolor=DARK_BG,
                      font=dict(color="#94a3b8"), margin=dict(l=30, r=30, t=40, b=10))
    return fig


# =====================================
# REVENUE KPI CARD HTML
# =====================================

def rev_kpi(label, value_str, delta_str, color_cls, badge_text, badge_cls):
    return f"""
<div class="rev-kpi-card">
  <div class="rev-kpi-label">
    {label}
    <span class="badge {badge_cls}">{badge_text}</span>
  </div>
  <div class="rev-kpi-value {color_cls}">{value_str}</div>
  <div class="rev-kpi-delta">{delta_str}</div>
</div>
"""


# =====================================
# REVENUE TAB RENDERER
# =====================================

def render_revenue_tab(rev):
    kpis            = rev.get("kpis", {})
    total_loss      = kpis.get("total_loss", 0)
    total_expected  = kpis.get("total_expected", 0)
    total_collected = kpis.get("total_collected", 0)
    collection_rate = kpis.get("collection_rate", 0)
    loss_change     = kpis.get("loss_change_vs_prev", 0)
    rate_change     = kpis.get("rate_change_vs_prev", 0)
    annual_loss     = total_loss * 12
    num_properties  = len(rev.get("rental_loss_by_property", []))

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(rev_kpi("Total Rental Loss / Mo", fmt_inr(total_loss),
            f"{'▲' if loss_change > 0 else '▼'} {fmt_inr(abs(loss_change))} vs prev",
            "color-red", "Revenue leak", "badge-red"), unsafe_allow_html=True)
    with c2:
        st.markdown(rev_kpi("Properties w/ Loss", str(num_properties), "Requires attention",
            "color-yellow", "Action needed", "badge-yellow"), unsafe_allow_html=True)
    with c3:
        st.markdown(rev_kpi("Collection Rate", f"{collection_rate:.1f}%",
            f"{'▲' if rate_change >= 0 else '▼'} {abs(rate_change):.1f}% MoM",
            "color-green", "MoM tracking", "badge-green"), unsafe_allow_html=True)
    with c4:
        st.markdown(rev_kpi("Projected Loss (12M)", fmt_inr(annual_loss), "if trend holds",
            "color-purple", "Projection", "badge-purple"), unsafe_allow_html=True)
    with c5:
        st.markdown(rev_kpi("Total Expected Rent", fmt_inr(total_expected),
            f"Collected: {fmt_inr(total_collected)}",
            "color-blue", "Current month", "badge-blue"), unsafe_allow_html=True)

    st.markdown('<div class="section-label">Loss Analysis</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(create_rental_loss_breakdown_donut(rev.get("rental_loss_breakdown", [])),
                        use_container_width=True)
    with col2:
        st.plotly_chart(create_collection_rate_gauge(collection_rate), use_container_width=True)
        st.markdown('<div class="section-label">Loss by Unit Type</div>', unsafe_allow_html=True)
        unit_data = rev.get("rental_loss_by_unit_type", [])
        if unit_data:
            udf = pd.DataFrame(unit_data)[["unit_type", "expected", "collected", "loss", "collection_rate"]]
            udf.columns = ["Unit Type", "Expected", "Collected", "Loss", "Rate %"]
            udf["Expected"]  = udf["Expected"].apply(fmt_inr)
            udf["Collected"] = udf["Collected"].apply(fmt_inr)
            udf["Loss"]      = udf["Loss"].apply(fmt_inr)
            st.dataframe(udf, use_container_width=True, hide_index=True, height=190)
        else:
            st.info("No unit type data.")

    st.markdown('<div class="section-label">Trends</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(create_rental_loss_trend(rev.get("monthly_rent_trend", [])), use_container_width=True)
    with col4:
        st.plotly_chart(create_income_expense_trend(rev.get("income_expense_trend", [])), use_container_width=True)

    st.markdown('<div class="section-label">Property Breakdown</div>', unsafe_allow_html=True)
    st.plotly_chart(create_loss_by_property_chart(rev.get("rental_loss_by_property", [])), use_container_width=True)


# =====================================
# LEADS TAB RENDERER  ← UPDATED
# =====================================

def render_leads_tab(leads):
    metrics      = leads.get("metrics", {})
    funnel_rates = leads.get("funnel_rates", {})
    coverage     = leads.get("vacant_unit_coverage", {})
    low_conv     = leads.get("low_conversion_units", [])

    # ── Row 1: Core Metrics ───────────────────────────────────
    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Active Leads",  metrics.get("total_leads", 0))
    c2.metric("Today's New Leads",   metrics.get("todays_new_leads", 0))
    c3.metric("Converted Leads",     metrics.get("converted_leads", 0))
    c4.metric("Conversion Rate",     f"{metrics.get('conversion_rate', 0):.1f}%")

    # ── Row 2: Funnel Rate Pills ──────────────────────────────
    st.markdown('<div class="section-label">Conversion Funnel Rates</div>', unsafe_allow_html=True)
    p1, p2, p3, p4, p5 = st.columns(5)

    def pill(col, label, value, sub, color):
        col.markdown(f"""
        <div class="funnel-pill">
            <div class="funnel-pill-label">{label}</div>
            <div class="funnel-pill-value" style="color:{color}">{value}</div>
            <div class="funnel-pill-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    pill(p1, "Lead → Enquiry",
         f"{funnel_rates.get('lead_to_enquiry_pct', 0):.1f}%",
         f"{funnel_rates.get('converted_to_enquiry', 0)} enquiries",
         "#38bdf8")
    pill(p2, "Enquiry → Tenant",
         f"{funnel_rates.get('enquiry_to_tenant_pct', 0):.1f}%",
         f"{funnel_rates.get('converted_to_tenant', 0)} tenants",
         "#34d399")
    pill(p3, "Lead → Tenant",
         f"{funnel_rates.get('lead_to_tenant_conversion_pct', 0):.1f}%",
         "Overall conversion",
         "#818cf8")
    pill(p4, "Converted to Enquiry",
         str(funnel_rates.get("converted_to_enquiry", 0)),
         "out of total leads",
         "#fbbf24")
    pill(p5, "Converted to Tenant",
         str(funnel_rates.get("converted_to_tenant", 0)),
         "out of total leads",
         "#a78bfa")

    # ── Row 3: Funnel chart + Ratings ────────────────────────
    st.markdown('<div class="section-label">Stage Breakdown</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(
        create_funnel_chart(leads.get("conversion_funnel", {})),
        use_container_width=True,
    )
    col2.plotly_chart(
        create_ratings_chart(leads.get("ratings_breakdown", [])),
        use_container_width=True,
    )

    # ── Row 4: Vacant Unit Coverage ──────────────────────────
    st.markdown('<div class="section-label">Vacant Unit Lead Coverage (Last 30 Days)</div>',
                unsafe_allow_html=True)

    verdict = coverage.get("sufficiency_verdict", "—")
    verdict_css = {
        "No Leads at All": "verdict-no-leads",
        "Insufficient":    "verdict-insufficient",
        "Sufficient":      "verdict-sufficient",
        "Well Covered":    "verdict-well-covered",
    }.get(verdict, "")
    verdict_color = {
        "No Leads at All": "#f87171",
        "Insufficient":    "#fbbf24",
        "Sufficient":      "#38bdf8",
        "Well Covered":    "#34d399",
    }.get(verdict, "#94a3b8")

    vc1, vc2, vc3, vc4 = st.columns(4)
    vc1.metric("Total Vacant Units",       coverage.get("total_vacant_units", 0))
    vc2.metric("Units with Leads",         coverage.get("vacant_units_with_leads", 0))
    vc3.metric("Units with No Leads",      coverage.get("vacant_units_with_no_leads", 0))
    vc4.metric("Avg Leads / Vacant Unit",  coverage.get("avg_leads_per_vacant_unit", 0))

    gauge_col, verdict_col = st.columns([2, 1])
    with gauge_col:
        st.plotly_chart(
            create_vacant_coverage_gauge(
                coverage.get("pct_units_covered", 0), verdict
            ),
            use_container_width=True,
        )
    with verdict_col:
        st.markdown(f"""
        <div class="verdict-card {verdict_css}" style="margin-top:40px">
            <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;color:#475569;margin-bottom:8px">
                Coverage Verdict
            </div>
            <div style="font-family:'Space Mono',monospace;font-size:1.3rem;font-weight:700;color:{verdict_color}">
                {verdict}
            </div>
            <div style="font-size:0.72rem;color:#64748b;margin-top:8px">
                {coverage.get('pct_units_covered', 0):.1f}% of vacant units
                have at least one recent lead
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Row 5: Low Conversion Units ──────────────────────────
    st.markdown('<div class="section-label">Hot-Lead Units with Low Conversion</div>',
                unsafe_allow_html=True)

    if low_conv:
        chart = create_low_conversion_chart(low_conv)
        if chart:
            st.plotly_chart(chart, use_container_width=True)

        df_lc = pd.DataFrame(low_conv)
        df_lc = df_lc[["property_name", "unit_code", "unit_description",
                        "total_hot_leads", "conversions", "conversion_rate_pct", "conversion_flag"]]
        df_lc.columns = ["Property", "Unit", "Description",
                         "Hot Leads", "Conversions", "Conv. Rate %", "Flag"]

        def flag_color(val):
            return "color: #f87171" if val == "Low Conversion" else "color: #34d399"

        st.dataframe(
            df_lc.style.applymap(flag_color, subset=["Flag"]),
            use_container_width=True,
            hide_index=True,
            height=300,
        )
    else:
        st.success("✅ No hot-lead units with low conversion detected.")

    # ── Row 6: Recent Activity ────────────────────────────────
    st.markdown('<div class="section-label">Recent Lead Activity</div>', unsafe_allow_html=True)
    recent = fetch_recent_leads()
    if recent:
        df = pd.DataFrame(recent)
        st.dataframe(df, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("No recent leads found.")


# =====================================
# MAIN APP
# =====================================

def main():
    st.markdown(
        '<p class="main-header">📊 TERP Analytics Dashboard</p>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.header("⚙️ Settings")
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")
        st.markdown(f"Last Updated: `{datetime.now().strftime('%H:%M:%S')}`")

    leads   = fetch_leads_dashboard()
    vacancy = fetch_vacancy_dashboard()
    revenue = fetch_revenue_dashboard()

    lead_metrics = (leads   or {}).get("metrics", {})
    vac_summary  = (vacancy or {}).get("summary", {})
    rev_kpis     = (revenue or {}).get("kpis", {})

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Units",     vac_summary.get("total_units", "—"))
    c2.metric("Vacancy Rate",    f"{vac_summary.get('vacancy_rate', 0):.1f}%")
    c3.metric("Active Leads",    lead_metrics.get("total_leads", "—"))
    c4.metric("Collection Rate", f"{rev_kpis.get('collection_rate', 0):.1f}%")
    c5.metric("Monthly Loss",    fmt_inr(rev_kpis.get("total_loss", 0)))

    tab_vac, tab_rev, tab_leads = st.tabs([
        "🏢  VACANCY",
        "💰  REVENUE & RENT",
        "🎯  LEADS",
    ])

    with tab_vac:
        if not vacancy:
            st.error("Unable to load vacancy data.")
        else:
            col1, col2 = st.columns(2)
            trend_data = vacancy.get("vacancy_trend")
            if trend_data:
                col1.plotly_chart(create_vacancy_trend_chart(trend_data), use_container_width=True)
            else:
                col1.plotly_chart(
                    create_duration_bucket_chart(vacancy.get("vacancy_duration_buckets", [])),
                    use_container_width=True)
            col2.plotly_chart(
                create_vacancy_by_property_chart(vacancy.get("vacancy_by_property", [])),
                use_container_width=True)
            st.plotly_chart(
                create_unit_type_chart(vacancy.get("vacancy_by_unit_type", [])),
                use_container_width=True)

    with tab_rev:
        if not revenue:
            st.error("Unable to load revenue data.")
            st.info(
                "Register the router in `app/api/v1/api.py`:\n\n"
                "```python\nfrom app.api.v1.endpoints import revenue_dashboard\n"
                "api_router.include_router(\n    revenue_dashboard.router,\n"
                "    prefix='/revenue-dashboard',\n    tags=['Revenue Dashboard']\n)\n```"
            )
        else:
            render_revenue_tab(revenue)

    with tab_leads:
        if not leads:
            st.error("Unable to load leads data.")
        else:
            render_leads_tab(leads)

    if auto_refresh:
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()