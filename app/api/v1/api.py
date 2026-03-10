# app/api/v1/api.py (or wherever you register routes)
from fastapi import APIRouter
from app.api.leads_dashboard import dashboard
from app.api.leads_dashboard import dashboard_vac
from app.api.leads_dashboard import revenue_dashboard
api_router = APIRouter()

# Register leads dashboard
api_router.include_router(
    dashboard.router,
    prefix="/leads-dashboard",
    tags=["Leads Dashboard"]
)

# Register vacancy dashboard
api_router.include_router(
    dashboard_vac.router,
    prefix="/vacancy-dashboard",
    tags=["Vacancy Dashboard"]
)
api_router.include_router(
    revenue_dashboard.router,
    prefix="/revenue-dashboard",
    tags=["Revenue Dashboard"]
)
