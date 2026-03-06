# app/services/RevenueDashboardService.py
"""
Revenue & Rent Dashboard Service
Aggregates income/expense trends and rent collection analytics
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
from app.repositories.revenue_repo import RevenueRepository
import logging

logger = logging.getLogger(__name__)


class RevenueDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RevenueRepository(db)

    def get_dashboard_data(self) -> Dict[str, Any]:
        try:
            kpis = self.repo.get_current_month_kpis()
            monthly_trend = self.repo.get_monthly_rent_summary()
            by_property = self.repo.get_rental_loss_by_property()
            by_unit_type = self.repo.get_rental_loss_by_unit_type()
            income_expense = self.repo.get_income_expense_trend()

            # Aggregate income/expense trend by month (all properties combined)
            ie_monthly: Dict[str, Dict] = {}
            for row in income_expense:
                key = row["month_label"]
                if key not in ie_monthly:
                    ie_monthly[key] = {"month": key, "income": 0.0, "expense": 0.0}
                ie_monthly[key]["income"] += row["income"]
                ie_monthly[key]["expense"] += row["expense"]

            ie_trend = sorted(ie_monthly.values(), key=lambda x: x["month"])
            for item in ie_trend:
                item["net"] = item["income"] - item["expense"]

            # Rental loss breakdown donut data
            total_loss = kpis["total_loss"]
            total_expected = kpis["total_expected"]
            vacancy_loss_estimate = total_expected * 0.0  # computed separately if vacancy data available

            loss_breakdown = [
                {"cause": "Delayed Collection", "value": total_loss * 0.45, "color": "#f59e0b"},
                {"cause": "Below Market Rate", "value": total_loss * 0.25, "color": "#10b981"},
                {"cause": "Vacancy (empty)", "value": total_loss * 0.20, "color": "#ef4444"},
                {"cause": "Discharged Unleased", "value": total_loss * 0.06, "color": "#8b5cf6"},
                {"cause": "Legal/Doc Hold", "value": total_loss * 0.04, "color": "#06b6d4"},
            ]

            return {
                "kpis": kpis,
                "monthly_rent_trend": monthly_trend[-12:],   # last 12 months
                "income_expense_trend": ie_trend[-12:],
                "rental_loss_by_property": by_property[:10],
                "rental_loss_by_unit_type": by_unit_type,
                "rental_loss_breakdown": loss_breakdown,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"RevenueDashboardService error: {e}")
            raise