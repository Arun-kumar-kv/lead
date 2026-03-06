from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime

from app.models.vacancy_reflected_models import (
    TerpPropertyUnits,
    TerpProperty,
    TerpPropertyUnitStatus,
    TerpPropertyUnitType,
    
)
from sqlalchemy import text
# from app.models.vacancy_reflected_models import TerpUnitShifting
from datetime import timedelta
class VacancyRepository:
    """
    Vacancy Repository (STATUS-DRIVEN)

    Source tables:
    - TERP_LS_PROPERTY_UNIT              -> TerpPropertyUnits
    - TERP_LS_PROPERTY                   -> TerpProperty
    - TERP_LS_PROPERTY_UNIT_STATUS       -> TerpPropertyUnitStatus
    - TERP_LS_PROPERTY_UNIT_TYPE         -> TerpPropertyUnitType
    - TERP_LS_UNIT_SHIFTING              -> TerpUnitShifting
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================
    # BASIC METRICS
    # ==========================================================

    def get_total_units_live(self) -> int:
        """Total units in system"""
        return (
            self.db.query(func.count(TerpPropertyUnits.ID))
            .scalar()
            or 0
        )

    def get_vacant_units_live(self) -> int:
        """Units where STATUS = 'Available'"""
        return (
            self.db.query(func.count(TerpPropertyUnits.ID))
            .join(
                TerpPropertyUnitStatus,
                TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID
            )
            .filter(TerpPropertyUnitStatus.STATUS == "Available")
            .scalar()
            or 0
        )

    def get_occupied_units_live(self) -> int:
        """Units where STATUS = 'Leased'"""
        return (
            self.db.query(func.count(TerpPropertyUnits.ID))
            .join(
                TerpPropertyUnitStatus,
                TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID
            )
            .filter(TerpPropertyUnitStatus.STATUS == "Leased")
            .scalar()
            or 0
        )

    def get_booked_units_live(self) -> int:
        """Units in booking states"""
        return (
            self.db.query(func.count(TerpPropertyUnits.ID))
            .join(
                TerpPropertyUnitStatus,
                TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID
            )
            .filter(
                TerpPropertyUnitStatus.STATUS.in_(
                    ["Booked", "Reserved", "Temporarily Booked"]
                )
            )
            .scalar()
            or 0
        )

    def get_vacancy_rate_live(self) -> float:
        """Vacancy % = Available / Total"""
        total = self.get_total_units_live()
        if total == 0:
            return 0.0

        vacant = self.get_vacant_units_live()
        return round((vacant / total) * 100, 2)
    def get_rent_ready_unleased_live(self) -> int:
        """
        Rent-ready unleased units
        (STATUS = 'Available')
        """
        return (
            self.db.query(func.count(TerpPropertyUnits.ID))
            .join(
                TerpPropertyUnitStatus,
                TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID
            )
            .filter(TerpPropertyUnitStatus.STATUS == "Available")
            .scalar()
            or 0
        )
    def get_maintenance_downtime_units_live(self) -> int:
        """
        Units blocked due to maintenance
        (Not implemented in status-driven model)
        """
        return 0
    def get_avg_vacancy_days_live(self) -> float:
        """
        Average days units have been vacant
        Based on LAST_UPDATED_AT
        """

        result = (
            self.db.query(
                func.avg(
                    func.datediff(
                        func.current_date(),
                        TerpPropertyUnits.LAST_UPDATED_AT
                    )
                )
            )
            .join(
                TerpPropertyUnitStatus,
                TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID
            )
            .filter(
                TerpPropertyUnitStatus.STATUS == "Available",
                TerpPropertyUnits.LAST_UPDATED_AT.isnot(None)
            )
            .scalar()
        )

        return round(float(result), 2) if result else 0.0
    # def get_re_leased_in_period_live(self, days: int = 30) -> int:
    #     """
    #     Units re-leased in last N days
    #     Based on MOVE_IN_DATE
    #     """

    #     cutoff_date = datetime.utcnow().date() - timedelta(days=days)

    #     try:
    #         return (
    #             self.db.query(func.count(TerpUnitShifting.ID))
    #             .filter(
    #                 TerpUnitShifting.MOVE_IN_DATE >= cutoff_date
    #             )
    #             .scalar()
    #             or 0
    #         )
    #     except Exception as e:
    #         logger.warning(f"Re-leased query failed: {e}")
    #         return 0
    # ==========================================================
    # VACANCY BY PROPERTY
    # ==========================================================

    # def get_vacancy_by_property_live(self) -> List[Dict[str, Any]]:
    #     """Vacant / Occupied / Booked per property"""

    #     results = (
    #         self.db.query(
    #             TerpProperty.NAME.label("property_name"),

    #             func.sum(
    #                 case((TerpPropertyUnitStatus.STATUS == "Leased", 1), else_=0)
    #             ).label("occupied_units"),

    #             func.sum(
    #                 case((TerpPropertyUnitStatus.STATUS == "Available", 1), else_=0)
    #             ).label("vacant_units"),

    #             func.sum(
    #                 case(
    #                     (TerpPropertyUnitStatus.STATUS.in_(
    #                         ["Booked", "Reserved", "Temporarily Booked"]
    #                     ), 1),
    #                     else_=0
    #                 )
    #             ).label("booked_units"),
    #         )
    #         .join(TerpPropertyUnits,
    #               TerpProperty.ID == TerpPropertyUnits.PROPERTY_ID)
    #         .join(TerpPropertyUnitStatus,
    #               TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID)
    #         .group_by(TerpProperty.ID, TerpProperty.NAME)
    #         .order_by(text("vacant_units DESC"))
    #         .limit(10)
    #         .all()
    #     )

    #     return [
    #         {
    #             "property_name": row.property_name,
    #             "occupied_units": row.occupied_units or 0,
    #             "vacant_units": row.vacant_units or 0,
    #             "booked_units": row.booked_units or 0,
    #             "total_units": (row.occupied_units or 0)
    #                            + (row.vacant_units or 0)
    #                            + (row.booked_units or 0),
    #         }
    #         for row in results
    #     ]
    def get_vacancy_by_property_live(self) -> List[Dict[str, Any]]:
        """Vacant / Occupied / Booked per property"""

        results = (
            self.db.query(
                func.trim(TerpProperty.NAME).label("property_name"),  # remove trailing spaces

                func.sum(
                    case((TerpPropertyUnitStatus.STATUS == "Leased", 1), else_=0)
                ).label("occupied_units"),

                func.sum(
                    case((TerpPropertyUnitStatus.STATUS == "Available", 1), else_=0)
                ).label("vacant_units"),

                func.sum(
                    case(
                        (TerpPropertyUnitStatus.STATUS.in_(
                            ["Booked", "Reserved", "Temporarily Booked"]
                        ), 1),
                        else_=0
                    )
                ).label("booked_units"),
            )
            .join(TerpPropertyUnits,
                TerpProperty.ID == TerpPropertyUnits.PROPERTY_ID)
            .join(TerpPropertyUnitStatus,
                TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID)
            .group_by(TerpProperty.ID, TerpProperty.NAME)
            .order_by(
                text("vacant_units DESC"),
                TerpProperty.NAME.asc()   # stable sorting for ties
            )
           
            .all()
        )

        return [
            {
                "property_name": row.property_name,
                "occupied_units": row.occupied_units or 0,
                "vacant_units": row.vacant_units or 0,
                "booked_units": row.booked_units or 0,
                "total_units": (row.occupied_units or 0)
                            + (row.vacant_units or 0)
                            + (row.booked_units or 0),
            }
            for row in results
        ]
    # ==========================================================
    # VACANCY BY UNIT TYPE
    # ==========================================================
    def get_vacancy_by_unit_type_live(self) -> List[Dict[str, Any]]:

        results = (
            self.db.query(
                TerpPropertyUnitType.NAME.label("unit_type"),

                func.count(TerpPropertyUnits.ID).label("total_units"),

                func.sum(
                    case(
                        (TerpPropertyUnitStatus.STATUS == "Available", 1),
                        else_=0
                    )
                ).label("vacant_units"),

                func.sum(
                    case(
                        (TerpPropertyUnitStatus.STATUS == "Leased", 1),
                        else_=0
                    )
                ).label("occupied_units"),

                func.sum(
                    case(
                        (
                            TerpPropertyUnitStatus.STATUS.in_(
                                ["Booked", "Reserved", "Temporarily Booked"]
                            ),
                            1
                        ),
                        else_=0
                    )
                ).label("booked_units"),
            )
            .select_from(TerpPropertyUnits)
            .join(
                TerpPropertyUnitStatus,
                TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID
            )
            .join(
                TerpPropertyUnitType,
                TerpPropertyUnits.UNIT_TYPE == TerpPropertyUnitType.ID
            )
            .group_by(TerpPropertyUnitType.NAME)
            .order_by(TerpPropertyUnitType.NAME)
            .all()
        )

        response = []

        for row in results:
            total_units = int(row.total_units or 0)
            vacant_units = int(row.vacant_units or 0)
            occupied_units = int(row.occupied_units or 0)
            booked_units = int(row.booked_units or 0)

            vacancy_percentage = (
                round((vacant_units * 100) / total_units, 2)
                if total_units > 0 else 0.0
            )

            response.append({
                "unit_type": row.unit_type,
                "total_units": total_units,
                "vacant_units": vacant_units,
                "occupied_units": occupied_units,
                "booked_units": booked_units,
                "vacancy_percentage": vacancy_percentage
            })

        return response
    # def get_vacancy_by_unit_type_live(self) -> List[Dict[str, Any]]:
    #     """Vacancy breakdown by unit type"""

    #     results = (
    #         self.db.query(
    #             TerpPropertyUnitType.NAME.label("unit_type"),
    #             func.count().label("total_units"),

    #             func.sum(
    #                 case((TerpPropertyUnitStatus.STATUS == "Available", 1), else_=0)
    #             ).label("vacant_units"),

    #             func.sum(
    #                 case((TerpPropertyUnitStatus.STATUS == "Leased", 1), else_=0)
    #             ).label("occupied_units"),

    #             func.sum(
    #                 case(
    #                     (TerpPropertyUnitStatus.STATUS.in_(
    #                         ["Booked", "Reserved", "Temporarily Booked"]
    #                     ), 1),
    #                     else_=0
    #                 )
    #             ).label("booked_units"),
    #         )
    #         .join(TerpPropertyUnitStatus,
    #               TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID)
    #         .join(TerpPropertyUnitType,
    #               TerpPropertyUnits.UNIT_TYPE == TerpPropertyUnitType.ID)
    #         .group_by(TerpPropertyUnitType.NAME)
    #         .order_by(TerpPropertyUnitType.NAME)
    #         .all()
    #     )

    #     return [
    #         {
    #             "unit_type": row.unit_type,
    #             "total_units": row.total_units,
    #             "vacant_units": row.vacant_units or 0,
    #             "occupied_units": row.occupied_units or 0,
    #             "booked_units": row.booked_units or 0,
    #             "vacancy_percentage": round(
    #                 (row.vacant_units / row.total_units) * 100, 2
    #             ) if row.total_units > 0 else 0.0
    #         }
    #         for row in results
    #     ]

    # ==========================================================
    # VACANCY DURATION BUCKETS
    # ==========================================================

    def get_vacancy_duration_buckets_live(self) -> Dict[str, int]:
        """Vacancy buckets based on LAST_UPDATED_AT"""

        today = func.current_date()

        results = (
            self.db.query(
                case(
                    (func.datediff(today, TerpPropertyUnits.LAST_UPDATED_AT).between(0, 30), "0-30 days"),
                    (func.datediff(today, TerpPropertyUnits.LAST_UPDATED_AT).between(31, 60), "31-60 days"),
                    (func.datediff(today, TerpPropertyUnits.LAST_UPDATED_AT).between(61, 90), "61-90 days"),
                    else_="90+ days"
                ).label("vacancy_bucket"),
                func.count().label("total")
            )
            .join(TerpPropertyUnitStatus,
                  TerpPropertyUnits.STATUS == TerpPropertyUnitStatus.ID)
            .filter(TerpPropertyUnitStatus.STATUS == "Available")
            .group_by("vacancy_bucket")
            .all()
        )

        return {row.vacancy_bucket: row.total for row in results}

    # ==========================================================
    # MOVE IN / MOVE OUT TREND
    # ==========================================================

    # def get_move_in_out_trend_live(self) -> List[Dict[str, Any]]:
    #     """Move-ins vs Move-outs grouped monthly"""

    #     results = (
    #         self.db.query(
    #             func.date_format(
    #                 func.coalesce(
    #                     TerpUnitShifting.MOVE_IN_DATE,
    #                     TerpUnitShifting.MOVE_OUT_DATE
    #                 ),
    #                 "%b"
    #             ).label("month"),

    #             func.year(
    #                 func.coalesce(
    #                     TerpUnitShifting.MOVE_IN_DATE,
    #                     TerpUnitShifting.MOVE_OUT_DATE
    #                 )
    #             ).label("year"),

    #             func.month(
    #                 func.coalesce(
    #                     TerpUnitShifting.MOVE_IN_DATE,
    #                     TerpUnitShifting.MOVE_OUT_DATE
    #                 )
    #             ).label("month_num"),

    #             func.count(
    #                 case((TerpUnitShifting.MOVEIN_STATUS == 1, 1))
    #             ).label("move_ins"),

    #             func.count(
    #                 case((TerpUnitShifting.MOVEOUT_STATUS == 1, 1))
    #             ).label("move_outs"),
    #         )
    #         .group_by("year", "month_num", "month")
    #         .order_by("year", "month_num")
    #         .all()
    #     )

    #     return [
    #         {
    #             "year": row.year,
    #             "month": row.month,
    #             "move_ins": row.move_ins,
    #             "move_outs": row.move_outs,
    #         }
    #         for row in results
    #     ]


    