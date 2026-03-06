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


# ============================================================================
# MAIN DASHBOARD ENDPOINT
# ============================================================================

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


# ============================================================================
# LIVE QUERIES (Real-time data)
# ============================================================================

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


# @router.get("/live/re-leased")
# async def get_re_leased_live(
#     days: int = Query(30, description="Period in days (30, 90, or 180)"),
#     db: Session = Depends(get_db)
# ):
#     """Get units re-leased in last N days (live query)"""
#     repo = VacancyRepository(db)
#     return {
#         "re_leased_count": repo.get_re_leased_in_period_live(days),
#         "period_days": days
#     }


# @router.get("/live/by-property")
# async def get_vacancy_by_property_live(db: Session = Depends(get_db)):
#     """
#     Get vacancy breakdown by property (live query)
    
#     **Response time:** 100-200ms
#     """
#     repo = VacancyRepository(db)
#     return {
#         "properties": repo.get_vacancy_by_property_live()
#     }
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


# ============================================================================
# SNAPSHOT QUERIES (Historical data - fast)
# ============================================================================

# @router.get("/trends/vacancy-rate")
# async def get_vacancy_rate_trend(
#     days: int = Query(365, description="Number of days to look back"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get vacancy rate trend from snapshots (fast)
    
#     **Response time:** 20-50ms
    
#     Returns up to 12 months of historical data
#     """
#     repo = VacancyRepository(db)
#     return {
#         "trend": repo.get_vacancy_trend_from_snapshot(days=days)
#     }


# @router.get("/trends/move-in-out")
# async def get_move_in_out_trend(
#     months: int = Query(12, description="Number of months to look back"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get move-in vs move-out seasonality from snapshots (fast)
    
#     **Response time:** 20-40ms
    
#     Shows 12-month pattern to identify peak churn months
#     """
#     repo = VacancyRepository(db)
#     return {
#         "trend": repo.get_move_in_out_trend_from_snapshot(months=months)
#     }


# @router.get("/snapshot/latest")
# async def get_latest_snapshot(db: Session = Depends(get_db)):
#     """
#     Get most recent daily snapshot
    
#     **Response time:** 10-20ms
#     """
#     repo = VacancyRepository(db)
#     snapshot = repo.get_latest_snapshot()
    
#     if not snapshot:
#         raise HTTPException(status_code=404, detail="No snapshot data available")
    
#     return {
#         "date": str(snapshot.DATE),
#         "total_units": snapshot.TOTAL_UNITS,
#         "vacant_units": snapshot.VACANT_UNITS,
#         "occupied_units": snapshot.OCCUPIED_UNITS,
#         "vacancy_rate": float(snapshot.VACANCY_RATE),
#         "avg_vacancy_days": float(snapshot.AVG_VACANCY_DAYS),
#         "rent_ready_unleased": snapshot.RENT_READY_UNLEASED,
#         "maintenance_downtime": snapshot.MAINTENANCE_DOWNTIME,
#         "re_leased_30d": snapshot.RE_LEASED_30D,
#         "duration_buckets": {
#             "0-30 days": snapshot.DURATION_0_30_DAYS,
#             "31-60 days": snapshot.DURATION_31_60_DAYS,
#             "61-90 days": snapshot.DURATION_61_90_DAYS,
#             "90+ days": snapshot.DURATION_90_PLUS_DAYS
#         },
#         "unit_types": {
#             "studio": snapshot.VACANT_STUDIO,
#             "1bhk": snapshot.VACANT_1BHK,
#             "2bhk": snapshot.VACANT_2BHK,
#             "3bhk": snapshot.VACANT_3BHK,
#             "commercial": snapshot.VACANT_COMMERCIAL
#         },
#         "monthly_loss": float(snapshot.MONTHLY_LOSS)
#     }


# @router.get("/snapshot/by-property")
# async def get_property_snapshot(
#     snapshot_date: Optional[date] = Query(None, description="Specific date (default: yesterday)"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get property-level vacancy from snapshot (fast)
    
#     **Response time:** 20-40ms
#     """
#     repo = VacancyRepository(db)
#     return {
#         "properties": repo.get_vacancy_by_property_from_snapshot(snapshot_date)
#     }


# @router.get("/snapshot/by-unit-type")
# async def get_unit_type_snapshot(
#     snapshot_date: Optional[date] = Query(None, description="Specific date (default: yesterday)"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get unit type vacancy from snapshot (fast)
    
#     **Response time:** 20-40ms
#     """
#     repo = VacancyRepository(db)
#     return {
#         "unit_types": repo.get_vacancy_by_unit_type_from_snapshot(snapshot_date)
#     }


# # ============================================================================
# # COMPARISON & ANALYSIS ENDPOINTS
# # ============================================================================

# @router.get("/compare/month-over-month")
# async def compare_month_over_month(db: Session = Depends(get_db)):
#     """
#     Compare current month vs previous month
    
#     Shows changes in:
#     - Vacant units
#     - Avg vacancy days
#     - Rent-ready unleased
#     - Re-leased count
#     """
#     # Implementation would compare latest snapshot with 30-days-ago snapshot
#     pass


# @router.get("/alerts/aging-units")
# async def get_aging_units_alert(
#     days_threshold: int = Query(90, description="Alert threshold in days"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get units vacant for more than threshold days
    
#     **Use case:** Identify units at risk, need urgent attention
#     """
#     # Implementation would query units with VACANT_SINCE > threshold
#     pass


# @router.get("/financial/impact")
# async def get_financial_impact(db: Session = Depends(get_db)):
#     """
#     Get financial impact analysis
    
#     Returns:
#     - Monthly revenue loss
#     - Annual projection
#     - Breakdown by property
#     - Breakdown by unit type
#     """
#     # Implementation would calculate revenue loss from vacant units
#     pass


# # ============================================================================
# # HEALTH CHECK
# # ============================================================================

# @router.get("/health")
# async def health_check(db: Session = Depends(get_db)):
#     """
#     Health check for vacancy dashboard
    
#     Verifies:
#     - Database connection
#     - Latest snapshot availability
#     - Data freshness
#     """
#     try:
#         repo = VacancyRepository(db)
#         snapshot = repo.get_latest_snapshot()
        
#         return {
#             "status": "healthy",
#             "database": "connected",
#             "latest_snapshot": str(snapshot.DATE) if snapshot else None,
#             "data_freshness": "ok" if snapshot and (
#                 (date.today() - snapshot.DATE).days <= 2
#             ) else "stale"
#         }
#     except Exception as e:
#         return {
#             "status": "unhealthy",
#             "error": str(e)
#         }