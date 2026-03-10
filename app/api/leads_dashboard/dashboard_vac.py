# app/api/v1/endpoints/vacancy_dashboard.py
"""
FastAPI endpoints for Vacancy Dashboard
Provides both complete dashboard data and individual metrics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.services.database import get_db
from app.services.VacancyDashboardService import VacancyDashboardService
from app.repositories.vacancy_repo import VacancyRepository

router = APIRouter()

# MAIN DASHBOARD ENDPOINT

@router.get("/")
async def get_vacancy_dashboard(db: Session = Depends(get_db)):
    """
    Get complete vacancy analytics dashboard
    
    **HYBRID APPROACH:**
    - Real-time: Current vacant units, avg days, live breakdowns
    - Historical: Trends, seasonality from snapshot tables
    
    **Response time:** 100-300ms (depends on data volume)
    
    **Returns:**
    - KPI cards (vacant units, avg days, rent-ready, re-leased, downtime)
    - Vacancy rate trend (12 months)
    - Vacancy by property (top 5)
    - Vacancy duration buckets
    - Vacancy by unit type
    - Move-in vs move-out seasonality
    - Financial impact
    """
    try:
        service = VacancyDashboardService(db)
        return service.get_dashboard_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# LIVE QUERIES (Real-time data)

@router.get("/live/summary")
async def get_live_summary(db: Session = Depends(get_db)):
    """
    Get current vacancy summary (live query)
    
    **Response time:** 50-100ms
    """
    repo = VacancyRepository(db)
    
    return {
        "total_units": repo.get_total_units_live(),
        "vacant_units": repo.get_vacant_units_live(),
        "occupied_units": repo.get_occupied_units_live(),
        "vacancy_rate": repo.get_vacancy_rate_live(),
        "avg_vacancy_days": repo.get_avg_vacancy_days_live()
    }


@router.get("/live/vacant-units")
async def get_vacant_units_live(db: Session = Depends(get_db)):
    """Get current vacant unit count (live query)"""
    repo = VacancyRepository(db)
    return {"vacant_units": repo.get_vacant_units_live()}


@router.get("/live/vacancy-rate")
async def get_vacancy_rate_live(db: Session = Depends(get_db)):
    """Get current vacancy rate (live query)"""
    repo = VacancyRepository(db)
    return {"vacancy_rate": repo.get_vacancy_rate_live()}


@router.get("/live/rent-ready")
async def get_rent_ready_live(db: Session = Depends(get_db)):
    """Get rent-ready unleased units count (live query)"""
    repo = VacancyRepository(db)
    return {
        "rent_ready_unleased": repo.get_rent_ready_unleased_live(),
        "maintenance_downtime": repo.get_maintenance_downtime_units_live()
    }


@router.get("/live/avg-vacancy-days")
async def get_avg_vacancy_days_live(db: Session = Depends(get_db)):
    """Get average vacancy duration (live query)"""
    repo = VacancyRepository(db)
    return {"avg_vacancy_days": repo.get_avg_vacancy_days_live()}


@router.get("/live/by-property")
async def get_vacancy_by_property_live(db: Session = Depends(get_db)):
    repo = VacancyRepository(db)

    return {
        "vacancy_by_property": {
            "title": "Vacancy by Property",
            "subtitle": "Live vacancy breakdown",
            "data": repo.get_vacancy_by_property_live(),
            "drill_available": True
        }
    }

@router.get("/live/by-unit-type")
async def get_vacancy_by_unit_type_live(db: Session = Depends(get_db)):
    """
    Get vacancy breakdown by unit type (live query)
    
    **Response time:** 80-150ms
    """
    repo = VacancyRepository(db)
    return {
        "unit_types": repo.get_vacancy_by_unit_type_live()
    }


@router.get("/live/duration-buckets")
async def get_duration_buckets_live(db: Session = Depends(get_db)):
    """
    Get vacancy duration distribution (live query)
    
    Returns count of units in each bucket:
    - 0-30 days
    - 31-60 days
    - 61-90 days
    - 90+ days
    """
    repo = VacancyRepository(db)
    return {
        "duration_buckets": repo.get_vacancy_duration_buckets_live()
    }

