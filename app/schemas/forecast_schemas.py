# app/schemas/forecast_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import date

ModelName = Literal["linear", "arima", "prophet", "ensemble"]


class ForecastPoint(BaseModel):
    month:     str = Field(..., example="2026-04")
    predicted: int
    lower:     int
    upper:     int


class ForecastResponse(BaseModel):
    model:             ModelName
    forecast_months:   int
    last_actual_month: str
    last_actual_value: int
    data:              List[ForecastPoint]
    model_comparison:  Optional[Dict[str, List[int]]] = None


class ActualPoint(BaseModel):
    month:      str
    lead_count: int


class ActualsResponse(BaseModel):
    total_months: int
    total_leads:  int
    data:         List[ActualPoint]


class CustomForecastRequest(BaseModel):
    months:     int            = Field(default=4, ge=1, le=12)
    model:      ModelName      = Field(default="ensemble")
    train_from: Optional[date] = None
    train_to:   Optional[date] = None

    model_config = {
        "json_schema_extra": {
            "example": {"months": 4, "model": "ensemble", "train_from": "2026-01-01"}
        }
    }