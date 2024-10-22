import requests
from pydantic import BaseModel
from typing import Optional


# Define the BuildingInsight model
class BuildingInsight(BaseModel):
    id: int
    installed_on: str
    lifetime_energy: str
    recent_month_energy: str
    energy_unit: str = "Wh"  # Default value if not provided

    def to_dict(self):
        return {
            "id": self.id,
            "installedOn": self.installed_on,
            "lifetimeEnergy": self.lifetime_energy,
            "recentMonthEnergy": self.recent_month_energy,
            "energyUnit": self.energy_unit
        }

    def __repr__(self) -> str:
        return (f"BuildingInsight(id={self.id}, installed_on={self.installed_on}, "
                f"lifetime_energy={self.lifetime_energy}, recent_month_energy={self.recent_month_energy}, "
                f"energy_unit={self.energy_unit})")