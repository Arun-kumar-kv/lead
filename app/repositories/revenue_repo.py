# # app/repositories/revenue_repo.py
# """
# Repository for Revenue & Rent analytics queries.
# Style mirrors leads_repo.py and vacancy_repo.py exactly:
#   - SQLAlchemy ORM (.query / .join / .filter / .group_by)
#   - func, case, and_ from sqlalchemy
#   - No raw text() SQL except where unavoidable (INTERVAL arithmetic)
# """

# from sqlalchemy.orm import Session
# from sqlalchemy import func, case, and_, text
# from typing import Dict, List, Any
# from datetime import date

# from app.models.revenue_reflected_models import (
#     TerpContract,
#     TerpContractChargesView,
#     TerpPaymentTerms,
#     TerpProperty,
#     TerpPropertyUnit,
#     TerpPropertyUnitType,
#     TerpAccVoucher,
#     TerpAccVoucherTransaction,
#     TerpAccChartLedgers,
#     TerpAccTenantReceipt,
#     TerpAccAmountType,
# )


# class RevenueRepository:
#     def __init__(self, db: Session):
#         self.db = db

#     # =========================================================
#     # 1️⃣  INCOME vs EXPENSE — grouped by CHART_ID + month
#     #      ACCOUNT_TYPE=3 + Cr  →  Income
#     #      ACCOUNT_TYPE=4 + Dr  →  Expense
#     # =========================================================

#     def get_income_expense_trend(self) -> List[Dict[str, Any]]:
#         """
#         Live query: Monthly income & expense per CHART_ID.
#         """
#         results = (
#             self.db.query(
#                 TerpAccVoucher.CHART_ID.label("chart_id"),
#                 func.year(TerpAccVoucher.VOUCHER_DATE).label("year"),
#                 func.month(TerpAccVoucher.VOUCHER_DATE).label("month"),
#                 func.sum(
#                     case(
#                         (
#                             and_(
#                                 TerpAccChartLedgers.ACCOUNT_TYPE == 4,
#                                 TerpAccVoucherTransaction.TYPE == "Dr",
#                             ),
#                             TerpAccVoucherTransaction.AMOUNT,
#                         ),
#                         else_=0,
#                     )
#                 ).label("expense"),
#                 func.sum(
#                     case(
#                         (
#                             and_(
#                                 TerpAccChartLedgers.ACCOUNT_TYPE == 3,
#                                 TerpAccVoucherTransaction.TYPE == "Cr",
#                             ),
#                             TerpAccVoucherTransaction.AMOUNT,
#                         ),
#                         else_=0,
#                     )
#                 ).label("income"),
#             )
#             .select_from(TerpAccVoucherTransaction)
#             .join(
#                 TerpAccVoucher,
#                 TerpAccVoucherTransaction.VOUCHER_ID == TerpAccVoucher.ID,
#             )
#             .join(
#                 TerpAccChartLedgers,
#                 TerpAccVoucherTransaction.LEDGER_ID == TerpAccChartLedgers.ID,
#             )
#             .filter(
#                 TerpAccVoucher.VOUCHER_DATE.isnot(None),
#                 TerpAccVoucher.IS_DRAFT == 0,
#             )
#             .group_by(
#                 TerpAccVoucher.CHART_ID,
#                 func.year(TerpAccVoucher.VOUCHER_DATE),
#                 func.month(TerpAccVoucher.VOUCHER_DATE),
#             )
#             .order_by(
#                 TerpAccVoucher.CHART_ID,
#                 func.year(TerpAccVoucher.VOUCHER_DATE),
#                 func.month(TerpAccVoucher.VOUCHER_DATE),
#             )
#             .all()
#         )

#         return [
#             {
#                 "chart_id": row.chart_id,
#                 "year": row.year,
#                 "month": row.month,
#                 "month_label": f"{row.year}-{str(row.month).zfill(2)}",
#                 "income": float(row.income or 0),
#                 "expense": float(row.expense or 0),
#                 "net": float((row.income or 0) - (row.expense or 0)),
#             }
#             for row in results
#         ]

#     # =========================================================
#     # 2️⃣  COLLECTED RENT — cleared tenant receipts of type Rent
#     #      Grouped by contract + calendar month
#     # =========================================================

#     def get_collected_rent_by_month(self) -> List[Dict[str, Any]]:
#         """
#         Live query: Collected rent per contract per calendar month.
#         Filters: IS_DRAFT=0, TYPE='Dr', CLEARENCE_STATUS=1, AMOUNT_TYPE='Rent'
#         """
#         results = (
#             self.db.query(
#                 TerpAccTenantReceipt.CONTRACT_ID.label("contract_id"),
#                 func.date_format(
#                     TerpAccVoucherTransaction.TRANSACTION_DATE, "%Y-%m"
#                 ).label("rent_month"),
#                 func.sum(TerpAccVoucherTransaction.AMOUNT).label("collected_rent"),
#             )
#             .select_from(TerpAccTenantReceipt)
#             .join(
#                 TerpAccVoucher,
#                 and_(
#                     TerpAccVoucher.ID == TerpAccTenantReceipt.VOUCHER_ID,
#                     TerpAccVoucher.IS_DRAFT == 0,
#                 ),
#             )
#             .join(
#                 TerpAccVoucherTransaction,
#                 and_(
#                     TerpAccVoucherTransaction.VOUCHER_ID == TerpAccVoucher.ID,
#                     TerpAccVoucherTransaction.TYPE == "Dr",
#                     TerpAccVoucherTransaction.CLEARENCE_STATUS == 1,
#                 ),
#             )
#             .join(
#                 TerpAccAmountType,
#                 and_(
#                     TerpAccAmountType.ID == TerpAccVoucherTransaction.AMOUNT_TYPE,
#                     TerpAccAmountType.AMOUNT_TYPE == "Rent",
#                 ),
#             )
#             .group_by(
#                 TerpAccTenantReceipt.CONTRACT_ID,
#                 func.date_format(
#                     TerpAccVoucherTransaction.TRANSACTION_DATE, "%Y-%m"
#                 ),
#             )
#             .all()
#         )

#         return [
#             {
#                 "contract_id": row.contract_id,
#                 "rent_month": row.rent_month,
#                 "collected_rent": float(row.collected_rent or 0),
#             }
#             for row in results
#         ]

#     # =========================================================
#     # 3️⃣  EXPECTED RENT — active contracts × payment instalments
#     #      The month-generator (n=0..5) is a Python loop so we
#     #      stay pure ORM without a cross-join on a literal subquery
#     # =========================================================

#     # Payment term name → (interval_months, instalment_count)
#     PAYMENT_TERM_MAP = {
#         "Single Payment": (12, 1),
#         "Two Payments":   (6,  2),
#         "Three Payments": (4,  3),
#         "Four Payments":  (3,  4),
#     }
#     DEFAULT_TERM = (3, 4)

#     def get_expected_rent_by_month(self) -> List[Dict[str, Any]]:
#         """
#         Live query: Expected rent instalment per contract per month.
#         Fetches all active contracts with their charge & payment term,
#         then expands instalments in Python (avoids INTERVAL cross-join).
#         """
#         from datetime import timedelta
#         import calendar

#         def add_months(dt: date, months: int) -> date:
#             """Add N months to a date, clamping to last day of target month."""
#             month = dt.month - 1 + months
#             year = dt.year + month // 12
#             month = month % 12 + 1
#             day = min(dt.day, calendar.monthrange(year, month)[1])
#             return date(year, month, day)

#         results = (
#             self.db.query(
#                 TerpContract.ID.label("contract_id"),
#                 TerpContract.PROPERTY_ID.label("property_id"),
#                 TerpProperty.NAME.label("property_name"),
#                 TerpPropertyUnit.ID.label("unit_id"),
#                 TerpPropertyUnit.CODE.label("unit_code"),
#                 TerpPropertyUnitType.NAME.label("unit_type"),
#                 TerpContractChargesView.START_DATE.label("start_date"),
#                 TerpContractChargesView.END_DATE.label("end_date"),
#                 TerpContractChargesView.TOTAL_AMOUNT.label("total_amount"),
#                 TerpPaymentTerms.NAME.label("payment_term"),
#             )
#             .select_from(TerpContract)
#             .join(TerpProperty, TerpProperty.ID == TerpContract.PROPERTY_ID)
#             .join(
#                 TerpContractChargesView,
#                 and_(
#                     TerpContractChargesView.CONTRACT_ID == TerpContract.ID,
#                     TerpContractChargesView.CHARGE_NAME == "Rent",
#                 ),
#             )
#             .outerjoin(
#                 TerpPropertyUnit,
#                 and_(
#                     TerpPropertyUnit.CODE == TerpContract.UNIT_MERGE_CODE,
#                     TerpPropertyUnit.PROPERTY_ID == TerpContract.PROPERTY_ID,
#                 ),
#             )
#             .outerjoin(
#                 TerpPropertyUnitType,
#                 TerpPropertyUnitType.ID == TerpPropertyUnit.UNIT_TYPE,
#             )
#             .outerjoin(
#                 TerpPaymentTerms,
#                 TerpPaymentTerms.ID == TerpContract.PAYMENT_TERM,
#             )
#             .filter(TerpContract.ACTIVE == 1)
#             .all()
#         )

#         today = date.today()
#         period_end = date(today.year, today.month,
#                           calendar.monthrange(today.year, today.month)[1])

#         rows: List[Dict[str, Any]] = []
#         for r in results:
#             interval_months, instalment_count = self.PAYMENT_TERM_MAP.get(
#                 r.payment_term, self.DEFAULT_TERM
#             )
#             expected_per_instalment = round(
#                 float(r.total_amount or 0) / instalment_count, 2
#             )
#             start = r.start_date if isinstance(r.start_date, date) else r.start_date.date()
#             end   = r.end_date   if isinstance(r.end_date,   date) else r.end_date.date()
#             cap   = min(end, period_end)

#             for n in range(6):          # mirrors n = 0..5 in original SQL
#                 instalment_date = add_months(start, n * interval_months)
#                 if instalment_date < start or instalment_date > cap:
#                     continue
#                 rows.append(
#                     {
#                         "contract_id":   r.contract_id,
#                         "property_id":   r.property_id,
#                         "property_name": r.property_name,
#                         "unit_id":       r.unit_id,
#                         "unit_code":     r.unit_code,
#                         "unit_type":     r.unit_type,
#                         "rent_month":    instalment_date.strftime("%Y-%m"),
#                         "expected_rent": expected_per_instalment,
#                     }
#                 )

#         return rows

#     # =========================================================
#     # 4️⃣  MERGED: Expected + Collected → full rent detail
#     #      Python-side join to keep both queries clean
#     # =========================================================

#     def get_rent_collection_detail(self) -> List[Dict[str, Any]]:
#         """
#         Combines expected and collected rent per (contract, month).
#         Returns one row per instalment with expected, collected & gap.
#         """
#         expected_rows = self.get_expected_rent_by_month()
#         collected_rows = self.get_collected_rent_by_month()

#         # lookup: (contract_id, rent_month) → collected_rent
#         collected_map: Dict[tuple, float] = {
#             (r["contract_id"], r["rent_month"]): r["collected_rent"]
#             for r in collected_rows
#         }

#         result = []
#         for r in expected_rows:
#             key = (r["contract_id"], r["rent_month"])
#             collected = collected_map.get(key, 0.0)
#             result.append(
#                 {
#                     **r,
#                     "collected_rent": collected,
#                     "uncollected": r["expected_rent"] - collected,
#                 }
#             )
#         return result

#     # =========================================================
#     # 5️⃣  MONTHLY SUMMARY — aggregate across all contracts
#     # =========================================================

#     def get_monthly_rent_summary(self) -> List[Dict[str, Any]]:
#         """
#         Live query: Total expected vs collected rent per month.
#         Used for Rental Loss Trend chart.
#         """
#         rows = self.get_rent_collection_detail()

#         monthly: Dict[str, Dict] = {}
#         for r in rows:
#             key = r["rent_month"]
#             if key not in monthly:
#                 monthly[key] = {"rent_month": key, "expected": 0.0, "collected": 0.0}
#             monthly[key]["expected"] += r["expected_rent"]
#             monthly[key]["collected"] += r["collected_rent"]

#         result = []
#         for m in sorted(monthly.values(), key=lambda x: x["rent_month"]):
#             m["loss"] = m["expected"] - m["collected"]
#             m["collection_rate"] = (
#                 round(m["collected"] / m["expected"] * 100, 2)
#                 if m["expected"] > 0
#                 else 0.0
#             )
#             result.append(m)

#         return result

#     # =========================================================
#     # 6️⃣  RENTAL LOSS BY PROPERTY
#     # =========================================================

#     def get_rental_loss_by_property(self) -> List[Dict[str, Any]]:
#         """
#         Live query: Total uncollected rent grouped by property.
#         """
#         rows = self.get_rent_collection_detail()

#         by_property: Dict[str, Dict] = {}
#         for r in rows:
#             key = r["property_name"] or f"Property {r['property_id']}"
#             if key not in by_property:
#                 by_property[key] = {
#                     "property_name": key,
#                     "expected": 0.0,
#                     "collected": 0.0,
#                 }
#             by_property[key]["expected"] += r["expected_rent"]
#             by_property[key]["collected"] += r["collected_rent"]

#         result = []
#         for p in by_property.values():
#             p["loss"] = p["expected"] - p["collected"]
#             p["collection_rate"] = (
#                 round(p["collected"] / p["expected"] * 100, 2)
#                 if p["expected"] > 0
#                 else 0.0
#             )
#             result.append(p)

#         return sorted(result, key=lambda x: x["loss"], reverse=True)

#     # =========================================================
#     # 7️⃣  RENTAL LOSS BY UNIT TYPE
#     # =========================================================

#     def get_rental_loss_by_unit_type(self) -> List[Dict[str, Any]]:
#         """
#         Live query: Uncollected rent grouped by unit type.
#         """
#         rows = self.get_rent_collection_detail()

#         by_type: Dict[str, Dict] = {}
#         for r in rows:
#             key = r["unit_type"] or "Unknown"
#             if key not in by_type:
#                 by_type[key] = {"unit_type": key, "expected": 0.0, "collected": 0.0}
#             by_type[key]["expected"] += r["expected_rent"]
#             by_type[key]["collected"] += r["collected_rent"]

#         result = []
#         for t in by_type.values():
#             t["loss"] = t["expected"] - t["collected"]
#             t["collection_rate"] = (
#                 round(t["collected"] / t["expected"] * 100, 2)
#                 if t["expected"] > 0
#                 else 0.0
#             )
#             result.append(t)

#         return sorted(result, key=lambda x: x["loss"], reverse=True)

#     # =========================================================
#     # 8️⃣  CURRENT MONTH KPIs
#     # =========================================================

#     def get_current_month_kpis(self) -> Dict[str, Any]:
#         """
#         Live query: KPI snapshot for current and previous month.
#         """
#         today = date.today()
#         current_month = f"{today.year}-{str(today.month).zfill(2)}"
#         prev_month_date = (
#             date(today.year, today.month - 1, 1)
#             if today.month > 1
#             else date(today.year - 1, 12, 1)
#         )
#         prev_month = (
#             f"{prev_month_date.year}-{str(prev_month_date.month).zfill(2)}"
#         )

#         rows = self.get_monthly_rent_summary()
#         monthly_map = {r["rent_month"]: r for r in rows}

#         _empty = {"expected": 0.0, "collected": 0.0, "loss": 0.0, "collection_rate": 0.0}
#         curr = monthly_map.get(current_month, _empty)
#         prev = monthly_map.get(prev_month, _empty)

#         return {
#             "current_month": current_month,
#             "total_expected": curr["expected"],
#             "total_collected": curr["collected"],
#             "total_loss": curr["loss"],
#             "collection_rate": curr["collection_rate"],
#             "loss_change_vs_prev": curr["loss"] - prev["loss"],
#             "rate_change_vs_prev": curr["collection_rate"] - prev["collection_rate"],
#         }
#############
# app/repositories/revenue_repo.py
"""
Repository for Revenue & Rent analytics queries.
Style mirrors leads_repo.py and vacancy_repo.py exactly:
  - SQLAlchemy ORM (.query / .join / .filter / .group_by)
  - func, case, and_ from sqlalchemy
  - PostgreSQL-compatible date functions (extract, to_char) instead of MySQL ones
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, text
from typing import Dict, List, Any
from datetime import date

from app.models.revenue_reflected_models import (
    EqLsContract,
    EqLsContractCharges,
    EqLsPaymentTerms,
    EqLsProperty,
    EqLsPropertyUnit,
    EqLsPropertyUnitType,
    EqAccVoucher,
    EqAccVoucherTransaction,
    EqAccChartLedgers,
    EqAccTenantReceipt,
    EqAccAmountType,
)


class RevenueRepository:
    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # 1️⃣  INCOME vs EXPENSE — grouped by CHART_ID + month
    #      ACCOUNT_TYPE=3 + Cr  →  Income
    #      ACCOUNT_TYPE=4 + Dr  →  Expense
    # =========================================================

    def get_income_expense_trend(self) -> List[Dict[str, Any]]:
        """
        Live query: Monthly income & expense per CHART_ID.
        Uses PostgreSQL extract() instead of MySQL YEAR()/MONTH().
        """
        results = (
            self.db.query(
                EqAccVoucher.CHART_ID.label("chart_id"),
                func.extract("year",  EqAccVoucher.VOUCHER_DATE).label("year"),
                func.extract("month", EqAccVoucher.VOUCHER_DATE).label("month"),
                func.sum(
                    case(
                        (
                            and_(
                                EqAccChartLedgers.ACCOUNT_TYPE == 4,
                                EqAccVoucherTransaction.TYPE == "Dr",
                            ),
                            EqAccVoucherTransaction.AMOUNT,
                        ),
                        else_=0,
                    )
                ).label("expense"),
                func.sum(
                    case(
                        (
                            and_(
                                EqAccChartLedgers.ACCOUNT_TYPE == 3,
                                EqAccVoucherTransaction.TYPE == "Cr",
                            ),
                            EqAccVoucherTransaction.AMOUNT,
                        ),
                        else_=0,
                    )
                ).label("income"),
            )
            .select_from(EqAccVoucherTransaction)
            .join(
                EqAccVoucher,
                EqAccVoucherTransaction.VOUCHER_ID == EqAccVoucher.ID,
            )
            .join(
                EqAccChartLedgers,
                EqAccVoucherTransaction.LEDGER_ID == EqAccChartLedgers.ID,
            )
            .filter(
                EqAccVoucher.VOUCHER_DATE.isnot(None),
                EqAccVoucher.IS_DRAFT == 0,
            )
            .group_by(
                EqAccVoucher.CHART_ID,
                func.extract("year",  EqAccVoucher.VOUCHER_DATE),
                func.extract("month", EqAccVoucher.VOUCHER_DATE),
            )
            .order_by(
                EqAccVoucher.CHART_ID,
                func.extract("year",  EqAccVoucher.VOUCHER_DATE),
                func.extract("month", EqAccVoucher.VOUCHER_DATE),
            )
            .all()
        )

        return [
            {
                "chart_id":    row.chart_id,
                "year":        int(row.year),
                "month":       int(row.month),
                "month_label": f"{int(row.year)}-{str(int(row.month)).zfill(2)}",
                "income":      float(row.income  or 0),
                "expense":     float(row.expense or 0),
                "net":         float((row.income or 0) - (row.expense or 0)),
            }
            for row in results
        ]

    # =========================================================
    # 2️⃣  COLLECTED RENT — cleared tenant receipts of type Rent
    #      Grouped by contract + calendar month
    # =========================================================

    def get_collected_rent_by_month(self) -> List[Dict[str, Any]]:
        """
        Live query: Collected rent per contract per calendar month.
        Uses PostgreSQL to_char() instead of MySQL DATE_FORMAT().
        Filters: IS_DRAFT=0, TYPE='Dr', CLEARENCE_STATUS=1, AMOUNT_TYPE='Rent'
        """
        results = (
            self.db.query(
                EqAccTenantReceipt.CONTRACT_ID.label("contract_id"),
                func.to_char(
                    EqAccVoucherTransaction.TRANSACTION_DATE, "YYYY-MM"
                ).label("rent_month"),
                func.sum(EqAccVoucherTransaction.AMOUNT).label("collected_rent"),
            )
            .select_from(EqAccTenantReceipt)
            .join(
                EqAccVoucher,
                and_(
                    EqAccVoucher.ID == EqAccTenantReceipt.VOUCHER_ID,
                    EqAccVoucher.IS_DRAFT == 0,
                ),
            )
            .join(
                EqAccVoucherTransaction,
                and_(
                    EqAccVoucherTransaction.VOUCHER_ID == EqAccVoucher.ID,
                    EqAccVoucherTransaction.TYPE == "Dr",
                    EqAccVoucherTransaction.CLEARENCE_STATUS == 1,
                ),
            )
            .join(
                EqAccAmountType,
                and_(
                    EqAccAmountType.ID == EqAccVoucherTransaction.AMOUNT_TYPE,
                    EqAccAmountType.AMOUNT_TYPE == "Rent",
                ),
            )
            .group_by(
                EqAccTenantReceipt.CONTRACT_ID,
                func.to_char(
                    EqAccVoucherTransaction.TRANSACTION_DATE, "YYYY-MM"
                ),
            )
            .all()
        )

        return [
            {
                "contract_id":  row.contract_id,
                "rent_month":   row.rent_month,
                "collected_rent": float(row.collected_rent or 0),
            }
            for row in results
        ]

    # =========================================================
    # 3️⃣  EXPECTED RENT — active contracts × payment instalments
    # =========================================================

    PAYMENT_TERM_MAP = {
        "Single Payment": (12, 1),
        "Two Payments":   (6,  2),
        "Three Payments": (4,  3),
        "Four Payments":  (3,  4),
    }
    DEFAULT_TERM = (3, 4)

    def get_expected_rent_by_month(self) -> List[Dict[str, Any]]:
        """
        Live query: Expected rent instalment per contract per month.
        Fetches all active contracts with their charge & payment term,
        then expands instalments in Python (avoids INTERVAL cross-join).
        """
        import calendar

        def add_months(dt: date, months: int) -> date:
            month = dt.month - 1 + months
            year  = dt.year + month // 12
            month = month % 12 + 1
            day   = min(dt.day, calendar.monthrange(year, month)[1])
            return date(year, month, day)

        results = (
            self.db.query(
                EqLsContract.ID.label("contract_id"),
                EqLsContract.PROPERTY_ID.label("property_id"),
                EqLsProperty.NAME.label("property_name"),
                EqLsPropertyUnit.ID.label("unit_id"),
                EqLsPropertyUnit.CODE.label("unit_code"),
                EqLsPropertyUnitType.NAME.label("unit_type"),
                EqLsContractCharges.START_DATE.label("start_date"),
                EqLsContractCharges.END_DATE.label("end_date"),
                EqLsContractCharges.TOTAL_AMOUNT.label("total_amount"),
                EqLsPaymentTerms.NAME.label("payment_term"),
            )
            .select_from(EqLsContract)
            .join(EqLsProperty, EqLsProperty.ID == EqLsContract.PROPERTY_ID)
            .join(
                EqLsContractCharges,
                and_(
                    EqLsContractCharges.CONTRACT_ID == EqLsContract.ID,
                    EqLsContractCharges.CHARGE_NAME == "Rent",
                ),
            )
            .outerjoin(
                EqLsPropertyUnit,
                and_(
                    EqLsPropertyUnit.CODE == EqLsContract.UNIT_MERGE_CODE,
                    EqLsPropertyUnit.PROPERTY_ID == EqLsContract.PROPERTY_ID,
                ),
            )
            .outerjoin(
                EqLsPropertyUnitType,
                EqLsPropertyUnitType.ID == EqLsPropertyUnit.UNIT_TYPE,
            )
            .outerjoin(
                EqLsPaymentTerms,
                EqLsPaymentTerms.ID == EqLsContract.PAYMENT_TERM,
            )
            .filter(EqLsContract.ACTIVE == 1)
            .all()
        )

        today      = date.today()
        period_end = date(today.year, today.month,
                          __import__("calendar").monthrange(today.year, today.month)[1])

        rows: List[Dict[str, Any]] = []
        for r in results:
            interval_months, instalment_count = self.PAYMENT_TERM_MAP.get(
                r.payment_term, self.DEFAULT_TERM
            )
            expected_per_instalment = round(
                float(r.total_amount or 0) / instalment_count, 2
            )
            start = r.start_date if isinstance(r.start_date, date) else r.start_date.date()
            end   = r.end_date   if isinstance(r.end_date,   date) else r.end_date.date()
            cap   = min(end, period_end)

            for n in range(6):
                instalment_date = add_months(start, n * interval_months)
                if instalment_date < start or instalment_date > cap:
                    continue
                rows.append({
                    "contract_id":   r.contract_id,
                    "property_id":   r.property_id,
                    "property_name": r.property_name,
                    "unit_id":       r.unit_id,
                    "unit_code":     r.unit_code,
                    "unit_type":     r.unit_type,
                    "rent_month":    instalment_date.strftime("%Y-%m"),
                    "expected_rent": expected_per_instalment,
                })

        return rows

    # =========================================================
    # 4️⃣  MERGED: Expected + Collected → full rent detail
    # =========================================================

    def get_rent_collection_detail(self) -> List[Dict[str, Any]]:
        """
        Combines expected and collected rent per (contract, month).
        Returns one row per instalment with expected, collected & gap.
        """
        expected_rows  = self.get_expected_rent_by_month()
        collected_rows = self.get_collected_rent_by_month()

        collected_map: Dict[tuple, float] = {
            (r["contract_id"], r["rent_month"]): r["collected_rent"]
            for r in collected_rows
        }

        result = []
        for r in expected_rows:
            key       = (r["contract_id"], r["rent_month"])
            collected = collected_map.get(key, 0.0)
            result.append({
                **r,
                "collected_rent": collected,
                "uncollected":    r["expected_rent"] - collected,
            })
        return result

    # =========================================================
    # 5️⃣  MONTHLY SUMMARY
    # =========================================================

    def get_monthly_rent_summary(self) -> List[Dict[str, Any]]:
        """
        Live query: Total expected vs collected rent per month.
        Used for Rental Loss Trend chart.
        """
        rows = self.get_rent_collection_detail()

        monthly: Dict[str, Dict] = {}
        for r in rows:
            key = r["rent_month"]
            if key not in monthly:
                monthly[key] = {"rent_month": key, "expected": 0.0, "collected": 0.0}
            monthly[key]["expected"]  += r["expected_rent"]
            monthly[key]["collected"] += r["collected_rent"]

        result = []
        for m in sorted(monthly.values(), key=lambda x: x["rent_month"]):
            m["loss"] = m["expected"] - m["collected"]
            m["collection_rate"] = (
                round(m["collected"] / m["expected"] * 100, 2)
                if m["expected"] > 0 else 0.0
            )
            result.append(m)

        return result

    # =========================================================
    # 6️⃣  RENTAL LOSS BY PROPERTY
    # =========================================================

    def get_rental_loss_by_property(self) -> List[Dict[str, Any]]:
        """Live query: Total uncollected rent grouped by property."""
        rows = self.get_rent_collection_detail()

        by_property: Dict[str, Dict] = {}
        for r in rows:
            key = r["property_name"] or f"Property {r['property_id']}"
            if key not in by_property:
                by_property[key] = {"property_name": key, "expected": 0.0, "collected": 0.0}
            by_property[key]["expected"]  += r["expected_rent"]
            by_property[key]["collected"] += r["collected_rent"]

        result = []
        for p in by_property.values():
            p["loss"] = p["expected"] - p["collected"]
            p["collection_rate"] = (
                round(p["collected"] / p["expected"] * 100, 2)
                if p["expected"] > 0 else 0.0
            )
            result.append(p)

        return sorted(result, key=lambda x: x["loss"], reverse=True)

    # =========================================================
    # 7️⃣  RENTAL LOSS BY UNIT TYPE
    # =========================================================

    def get_rental_loss_by_unit_type(self) -> List[Dict[str, Any]]:
        """Live query: Uncollected rent grouped by unit type."""
        rows = self.get_rent_collection_detail()

        by_type: Dict[str, Dict] = {}
        for r in rows:
            key = r["unit_type"] or "Unknown"
            if key not in by_type:
                by_type[key] = {"unit_type": key, "expected": 0.0, "collected": 0.0}
            by_type[key]["expected"]  += r["expected_rent"]
            by_type[key]["collected"] += r["collected_rent"]

        result = []
        for t in by_type.values():
            t["loss"] = t["expected"] - t["collected"]
            t["collection_rate"] = (
                round(t["collected"] / t["expected"] * 100, 2)
                if t["expected"] > 0 else 0.0
            )
            result.append(t)

        return sorted(result, key=lambda x: x["loss"], reverse=True)

    # =========================================================
    # 8️⃣  CURRENT MONTH KPIs
    # =========================================================

    def get_current_month_kpis(self) -> Dict[str, Any]:
        """Live query: KPI snapshot for current and previous month."""
        today         = date.today()
        current_month = f"{today.year}-{str(today.month).zfill(2)}"
        prev_month_date = (
            date(today.year, today.month - 1, 1)
            if today.month > 1
            else date(today.year - 1, 12, 1)
        )
        prev_month = f"{prev_month_date.year}-{str(prev_month_date.month).zfill(2)}"

        rows        = self.get_monthly_rent_summary()
        monthly_map = {r["rent_month"]: r for r in rows}

        _empty = {"expected": 0.0, "collected": 0.0, "loss": 0.0, "collection_rate": 0.0}
        curr = monthly_map.get(current_month, _empty)
        prev = monthly_map.get(prev_month,    _empty)

        return {
            "current_month":       current_month,
            "total_expected":      curr["expected"],
            "total_collected":     curr["collected"],
            "total_loss":          curr["loss"],
            "collection_rate":     curr["collection_rate"],
            "loss_change_vs_prev": curr["loss"]            - prev["loss"],
            "rate_change_vs_prev": curr["collection_rate"] - prev["collection_rate"],
        }