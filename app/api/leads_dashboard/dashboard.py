# app/api/leads_dashboard/dashboard.py
from fastapi import APIRouter, Depends,Query
from sqlalchemy.orm import Session
from app.services.database import get_db
from app.services.LeadsDashboardService import LeadsDashboardService
from app.repositories.leads_repo import LeadsRepository
from app.services.LeadsForecastService import LeadsForecastService
from app.schemas.forecast_schemas import (
    ForecastResponse,
    ActualsResponse,
    CustomForecastRequest,
    ModelName,
)
router = APIRouter()

@router.get("/")
async def get_leads_dashboard(property_id:int = None,property_type: str = None,date_from:str = None,date_to:str = None,db: Session = Depends(get_db)):
    """
    Get complete leads analytics dashboard
    
    HYBRID APPROACH:
    - Real-time: Active leads, today's new leads, current ratings
    - Historical: Trends, conversion rates from snapshot tables
    
    Response time: 50-150ms
    """
    service = LeadsDashboardService(db)
    return service.get_dashboard_data(property_id=property_id,
        property_type=property_type,
        date_from=date_from,
        date_to=date_to,)

@router.get("/live/total")
async def get_total_leads_live(db: Session = Depends(get_db)):
    """Get total active leads (live query)"""
    repo = LeadsRepository(db)
    return {"total_leads": repo.get_total_leads_live()}

@router.get("/live/conversion-breakdown")
async def get_conversion_breakdown_live(db: Session = Depends(get_db)):
    """Get current conversion stage breakdown (live query)"""
    repo = LeadsRepository(db)
    return repo.get_conversion_breakdown_live()

@router.get("/live/ratings")
async def get_ratings_breakdown_live(db: Session = Depends(get_db)):
    """Get lead ratings breakdown (live query)"""
    repo = LeadsRepository(db)
    return {"ratings": repo.get_leads_by_ratings_live()}

@router.get("/live/recent")
async def get_recent_leads(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent lead inquiries (live query)"""
    repo = LeadsRepository(db)
    return {"recent_leads": repo.get_recent_leads_live(limit=limit)}

@router.get("/live/enquiry-conversion")
async def get_lead_to_enquiry_conversion(db: Session = Depends(get_db)):
    """
    Get lead → enquiry conversion rate.
    Returns total leads, how many converted to an enquiry, and the conversion %.
    """
    repo = LeadsRepository(db)
    return repo.get_lead_to_enquiry_conversion()


@router.get("/live/funnel")
async def get_full_funnel_conversion(db: Session = Depends(get_db)):
    """
    Get full conversion funnel rates.
    - Lead → Enquiry %
    - Enquiry → Tenant %
    - Lead → Tenant (overall) %
    """
    repo = LeadsRepository(db)
    return repo.get_full_funnel_conversion()


@router.get("/live/vacant-coverage")
async def get_vacant_units_lead_coverage(db: Session = Depends(get_db)):
    """
    Get lead coverage for vacant units over the last 30 days.
    Returns counts, coverage %, avg leads per unit, and a sufficiency verdict.
    """
    repo = LeadsRepository(db)
    return repo.get_vacant_units_lead_coverage()


@router.get("/live/low-conversion-units")
async def get_vacant_units_high_leads_low_conversion(db: Session = Depends(get_db)):
    """
    Get vacant units with high hot-lead volume but low conversion to tenant.
    Units with < 20% conversion rate are flagged as 'Low Conversion'.
    """
    repo = LeadsRepository(db)
    return {"units": repo.get_vacant_units_high_leads_low_conversion()}



@router.get("/live/active-inactive")
async def get_active_inactive_leads(db: Session = Depends(get_db)):
    """
    Get active vs inactive lead counts with percentages.
    """
    repo = LeadsRepository(db)
    return repo.get_active_inactive_leads_count()


@router.get("/live/new-leads-periods")
async def get_new_leads_periods(db: Session = Depends(get_db)):
    """
    Get new lead counts for today, this week, and this month.
    """
    repo = LeadsRepository(db)
    return repo.get_new_leads_periods()

@router.get("/live/leads-by-channel")
async def get_leads_by_channel(db: Session = Depends(get_db)):
    """
    Get lead count grouped by channel (Email, Walk in, Telephonic, etc.)
    """
    repo = LeadsRepository(db)
    return {
        "title": "Leads by Channel",
        "units": repo.get_leads_by_channel(),
    }


#forecast
@router.get("/forecast/actuals", response_model=ActualsResponse)
async def get_forecast_actuals(db: Session = Depends(get_db)):
    """Raw monthly lead counts used as forecast training data."""
    return LeadsForecastService(db).get_actuals()
 
@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    months: int       = Query(default=4, ge=1, le=12, description="Months ahead to forecast"),
    model:  ModelName = Query(default="ensemble",     description="linear | arima | prophet | ensemble"),
    db: Session = Depends(get_db),
):
    """Forecast lead volume for the next N months with 70% confidence intervals."""
    return LeadsForecastService(db).get_forecast(months=months, model=model)
 
@router.post("/forecast/custom", response_model=ForecastResponse)
async def get_forecast_custom(body: CustomForecastRequest, db: Session = Depends(get_db)):
    """Forecast with a custom training window e.g. train_from: 2026-01-01."""
    return LeadsForecastService(db).get_forecast(
        months=body.months,
        model=body.model,
        train_from=body.train_from,
        train_to=body.train_to,
    )









