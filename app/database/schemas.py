from pydantic import BaseModel
from datetime import datetime

class ItemCreate(BaseModel):
    date: datetime | None = None
    rate: float

class ItemUpdate(BaseModel):
    date: datetime | None = None
    rate: float | None = None

class Item(ItemCreate):
    id: int

    class Config:
        from_attributes = True