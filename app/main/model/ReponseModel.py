from pydantic import BaseModel
from typing import Any
class ReponseModel(BaseModel):
    message: Any
    status: int
    