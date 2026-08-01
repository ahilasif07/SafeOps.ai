from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SensorReadingCreate(BaseModel):
    machine_id: int
    sensor_type: str
    value: float
    unit: str

class SensorReadingOut(SensorReadingCreate):
    id: int
    is_anomaly: bool
    timestamp: datetime

    class Config:
        from_attributes = True
