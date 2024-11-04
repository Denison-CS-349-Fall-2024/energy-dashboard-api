from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool


class Site(BaseModel):
    id: str
    id_solar_edge: Optional[int] = None
    id_energy_star: Optional[int] = None
    name_solar_edge: Optional[str] = None
    name_energy_star: Optional[str] = None
    internal_name: str


class QuickInsightsType(str, Enum):
    solar = "solar"
    electric = "electric"
    natural_gas = "natural_gas"


class QuickInsights(BaseModel):
    id: str
    id_solar_edge: Optional[int] = None
    id_energy_star: Optional[int] = None
    installed_on: Optional[str] = None
    lifetime_energy: Optional[float] = None
    recent_month_energy: Optional[float] = None
    energy_unit: Optional[str] = None


class ChartType(str, Enum):
    Y = "Y"
    M = "M"
    D = "D"
    All = "All"


class ValueShape(BaseModel):
    # in this string "%Y-%m-%d %H:%M:%S"
    date: str
    value: float


class SourceShape(BaseModel):
    label: QuickInsightsType
    energy_unit: str
    # data = [{"date": datetime, "value": float}, ...]
    data: list[ValueShape]


class ChartData(BaseModel):
    id: str
    id_solar_edge: Optional[int] = None
    id_energy_star: Optional[int] = None
    chart_type: ChartType
    chart_date: Optional[date] = None
    sources: list[SourceShape]
