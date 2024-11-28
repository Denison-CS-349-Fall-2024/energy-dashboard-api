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
    internal_name: str
    id_solar_edge: Optional[int] = None
    id_energy_star: Optional[int] = None
    name_solar_edge: Optional[str] = None
    name_energy_star: Optional[str] = None
    custom_api_key: Optional[str] = None
    site_image_url: Optional[str] = None


class QuickInsightsType(str, Enum):
    solar = "solar"
    electric_grid = "electric_grid"
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


class EnvBenefitsData(BaseModel):
    total_co2_emission_saved: float
    total_trees_planted: float
    total_solar_sites: int
    co2_emission_saved_energy_unit: Optional[str] = "lbs"
    trees_planted_energy_unit: Optional[str] = None


class UploadedSolarEdgeSite(BaseModel):
    id_solar_edge: int
    name_solar_edge: str
    custom_api_key: str
    active: bool
