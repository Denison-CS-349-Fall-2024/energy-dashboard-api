from pydantic import BaseModel
class BuildingDocument(BaseModel):
    id: int
    name: str
    portfolio_id: int
    solarEdge_id: int

    def to_dict(self):
        return {
            "name": self.name,
            "portfolio_id": self.portfolio_id,
            "solarEdge_id": self.solarEdge_id,
            "id": self.id
        }
    
    def __repr__(self) -> str:
        return f"Building(name={self.name},portfolio_id={self.portfolio_id},solarEdge_id={self.solarEdge_id})"