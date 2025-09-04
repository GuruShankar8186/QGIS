from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

Coord = Tuple[float, float]

class PolygonIn(BaseModel):
    name: Optional[str]
    coordinates: List[Coord] = Field(..., description="Outer ring [lon, lat]")
    holes: Optional[List[List[Coord]]] = None

class PolygonsPayload(BaseModel):
    polygons: List[PolygonIn]
