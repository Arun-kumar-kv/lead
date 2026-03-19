# app/services/LeadsForecastService.py

import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from datetime import date
from typing import Optional, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.reflected_models import EqLsLeads
from app.schemas.forecast_schemas import (
    ModelName, ForecastResponse, ForecastPoint,
    ActualsResponse, ActualPoint,
)

from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

CI_ALPHA   = 0.30   # → 70% confidence interval
ARIMA_ORDERS = [(1, 1, 0), (0, 1, 0), (1, 0, 0)]   # fallback chain


class LeadsForecastService:

    def __init__(self, db: Session):
        self.db = db

    def get_actuals(self) -> ActualsResponse:
        df = self._fetch_series()
        return ActualsResponse(
            total_months=len(df),
            total_leads=int(df["y"].sum()),
            data=[
                ActualPoint(month=r.ds.strftime("%Y-%m"), lead_count=int(r.y))
                for r in df.itertuples()
            ],
        )

    def get_forecast(
        self,
        months: int,
        model: ModelName,
        train_from: Optional[date] = None,
        train_to:   Optional[date] = None,
    ) -> ForecastResponse:

        df = self._fetch_series(start=train_from, end=train_to)

        if len(df) < 3:
            raise HTTPException(
                status_code=422,
                detail=f"Only {len(df)} months of data. Need at least 3 to forecast.",
            )

        try:
            if model == "ensemble":
                # run all 3 individual models, then average
                individual = {
                    m: self._run_model(m, df, months)
                    for m in ("linear", "arima", "prophet")
                }
                pred, upper, lower = self._average_results(individual)
            else:
                # run just the requested model
                individual = None
                pred, upper, lower = self._run_model(model, df, months)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model error: {e}")

        return self._build_response(df, model, months, pred, upper, lower, individual)

    #single entry point for all models

    def _run_model(
        self, model: str, df: pd.DataFrame, n: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Single dispatcher — one function, any model name.
        Returns (pred, upper, lower) arrays of length n.
        """
        if model == "linear":
            return self._fit_linear(df, n)
        elif model == "arima":
            return self._fit_arima(df, n)
        elif model == "prophet":
            return self._fit_prophet(df, n)
        else:
            raise ValueError(f"Unknown model: {model!r}")

    #  fitters

    def _fit_linear(self, df: pd.DataFrame, n: int):
        X     = np.arange(len(df)).reshape(-1, 1)
        y     = df["y"].values
        m     = LinearRegression().fit(X, y)
        fx    = np.arange(len(df), len(df) + n).reshape(-1, 1)
        pred  = np.maximum(m.predict(fx), 0).round().astype(int)
        std   = np.std(y - m.predict(X))
        upper = (pred + 1.5 * std).round().astype(int)
        lower = np.maximum(pred - 1.5 * std, 0).round().astype(int)
        return pred, upper, lower

    def _fit_arima(self, df: pd.DataFrame, n: int):
        for order in ARIMA_ORDERS:
            try:
                m     = ARIMA(df["y"].values, order=order).fit()
                fc    = m.get_forecast(steps=n)
                pred  = np.maximum(fc.predicted_mean, 0).round().astype(int)
                ci    = fc.conf_int(alpha=CI_ALPHA)
                upper = np.maximum(ci[:, 1], 0).round().astype(int)
                lower = np.maximum(ci[:, 0], 0).round().astype(int)
                return pred, upper, lower
            except Exception:
                continue
        # hard fallback — repeat last known value
        last = int(df["y"].iloc[-1])
        pred = np.array([last] * n)
        return pred, pred + 20, np.maximum(pred - 20, 0)

    def _fit_prophet(self, df: pd.DataFrame, n: int):
        m = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.5,
            interval_width=1 - CI_ALPHA,
        )
        m.fit(df[["ds", "y"]])
        future = m.make_future_dataframe(periods=n, freq="MS")
        fc     = m.predict(future)
        fut    = fc[fc["ds"] > df["ds"].max()]
        pred   = np.maximum(fut["yhat"].values,       0).round().astype(int)
        upper  = np.maximum(fut["yhat_upper"].values, 0).round().astype(int)
        lower  = np.maximum(fut["yhat_lower"].values, 0).round().astype(int)
        return pred, upper, lower

    # ensemble helper

    def _average_results(self, individual: dict):
        """Average pred/upper/lower across all individual model results."""
        preds  = [v[0] for v in individual.values()]
        uppers = [v[1] for v in individual.values()]
        lowers = [v[2] for v in individual.values()]
        return (
            np.round(np.mean(preds,  axis=0)).astype(int),
            np.round(np.mean(uppers, axis=0)).astype(int),
            np.round(np.mean(lowers, axis=0)).astype(int),
        )

    # data layer

    def _fetch_series(
        self,
        start: Optional[date] = None,
        end:   Optional[date] = None,
    ) -> pd.DataFrame:
        date_col = None
        # for col_name in ("inquiry_date", "created_at", "updated_at"):
        for col_name in ("INQUIRY_DATE", "inquiry_date", "created_at", "updated_at"):
            if hasattr(EqLsLeads, col_name):
                date_col = getattr(EqLsLeads, col_name)
                break

        if date_col is None:
            raise HTTPException(
                status_code=500,
                detail="No date column on EqLsLeads (tried inquiry_date, created_at, updated_at).",
            )

        month_expr = func.date_trunc("month", date_col).label("month")
        q = (
            self.db.query(month_expr, func.count().label("lead_count"))
            .filter(date_col.isnot(None))
        )
        if start:
            q = q.filter(date_col >= start)
        if end:
            q = q.filter(date_col <= end)

        rows = q.group_by(month_expr).order_by(month_expr).all()

        if not rows:
            raise HTTPException(status_code=404, detail="No lead data found for that date range.")

        df = pd.DataFrame(rows, columns=["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)
        # df["ds"] = pd.to_datetime(df["ds"])
        df["y"]  = df["y"].astype(int)
        df = df.sort_values("ds").reset_index(drop=True)

        full_range = pd.date_range(df["ds"].min(), df["ds"].max(), freq="MS")
        df = (
            df.set_index("ds")
              .reindex(full_range, fill_value=0)
              .rename_axis("ds")
              .reset_index()
        )
        return df

    #  response builder

    def _build_response(
        self,
        df: pd.DataFrame,
        model: ModelName,
        months: int,
        pred: np.ndarray,
        upper: np.ndarray,
        lower: np.ndarray,
        individual: Optional[dict],
    ) -> ForecastResponse:

        future_dates = pd.date_range(
            df["ds"].max() + pd.DateOffset(months=1), periods=months, freq="MS"
        )
        points = [
            ForecastPoint(
                month=d.strftime("%Y-%m"),
                predicted=int(pred[i]),
                lower=int(lower[i]),
                upper=int(upper[i]),
            )
            for i, d in enumerate(future_dates)
        ]
        # model_comparison only populated for ensemble
        comparison = (
            {m: [int(v) for v in individual[m][0]] for m in individual}
            if individual else None
        )
        return ForecastResponse(
            model=model,
            forecast_months=months,
            last_actual_month=df["ds"].iloc[-1].strftime("%Y-%m"),
            last_actual_value=int(df["y"].iloc[-1]),
            data=points,
            model_comparison=comparison,
        )