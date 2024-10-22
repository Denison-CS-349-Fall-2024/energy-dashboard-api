from pydantic import BaseModel
class BuildingDocument(BaseModel):
    property_name: str
    portfolio_id: str
    solarEdge_id: str

    def to_dict(self):
        return {
            "property_name": self.property_name,
            "portfolio_id": self.portfolio_id,
            "solarEdge_id": self.solarEdge_id
        }
    
    def __repr__(self) -> str:
        return f"Building(property_name={self.property_name}, portfolio_id={self.portfolio_id},solarEdge_id={self.solarEdge_id})"