# app/api/v1/endpoints/revenue_dashboard.py
"""
FastAPI endpoints for Revenue & Rent Dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.database import get_db
from app.services.RevenueDashboardService import RevenueDashboardService
from app.repositories.revenue_repo import RevenueRepository

router = APIRouter()


@router.get("/")
async def get_revenue_dashboard(db: Session = Depends(get_db)):
    """
    Complete Revenue & Rent analytics dashboard.

    Returns:
    - KPI cards (expected rent, collected, loss, collection rate)
    - Monthly rent trend (expected vs collected vs loss)
    - Income vs expense trend
    - Rental loss by property
    - Rental loss by unit type
    - Rental loss breakdown donut
    """
    try:
        service = RevenueDashboardService(db)
        return service.get_dashboard_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live/kpis")
async def get_revenue_kpis(db: Session = Depends(get_db)):
    """Current month KPIs - expected, collected, loss, collection rate."""
    repo = RevenueRepository(db)
    return repo.get_current_month_kpis()


@router.get("/live/monthly-trend")
async def get_monthly_trend(db: Session = Depends(get_db)):
    """Monthly rent collection trend (last 12 months)."""
    repo = RevenueRepository(db)
    return {"trend": repo.get_monthly_rent_summary()}


@router.get("/live/loss-by-property")
async def get_loss_by_property(db: Session = Depends(get_db)):
    """Rental loss breakdown by property."""
    repo = RevenueRepository(db)
    return {"properties": repo.get_rental_loss_by_property()}


@router.get("/live/loss-by-unit-type")
async def get_loss_by_unit_type(db: Session = Depends(get_db)):
    """Rental loss breakdown by unit type."""
    repo = RevenueRepository(db)
    return {"unit_types": repo.get_rental_loss_by_unit_type()}


@router.get("/live/income-expense")
async def get_income_expense(db: Session = Depends(get_db)):
    """Monthly income vs expense trend."""
    repo = RevenueRepository(db)
    return {"trend": repo.get_income_expense_trend()}