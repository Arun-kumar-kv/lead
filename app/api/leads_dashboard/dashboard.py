# app/api/v1/endpoints/leads_dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.database import get_db
from app.services.LeadsDashboardService import LeadsDashboardService
from app.repositories.leads_repo import LeadsRepository

router = APIRouter()

@router.get("/")
async def get_leads_dashboard(db: Session = Depends(get_db)):
    """
    Get complete leads analytics dashboard
    
    HYBRID APPROACH:
    - Real-time: Active leads, today's new leads, current ratings
    - Historical: Trends, conversion rates from snapshot tables
    
    Response time: 50-150ms
    """
    service = LeadsDashboardService(db)
    return service.get_dashboard_data()

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

# @router.get("/trends/conversion")
# async def get_conversion_trend(days: int = 30, db: Session = Depends(get_db)):
#     """Get conversion rate trend (from snapshots - fast)"""
#     repo = LeadsRepository(db)
#     return {"trend": repo.get_conversion_trend_from_snapshot(days=days)}