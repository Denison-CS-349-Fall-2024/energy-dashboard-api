from pydantic import BaseModel
class PortfolioEnergy(BaseModel):
    date: str
    energy_usage: str
    unit: str
