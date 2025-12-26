from sqlalchemy import Column, Integer, DateTime, Float
from .db import Base
from datetime import datetime

class RateItem(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    rate = Column(Float, nullable=False)