from typing import List
from sqlalchemy.orm import Session
from app.models.sensor import SensorReading
from app.repositories.base import BaseRepository

class SensorRepository(BaseRepository[SensorReading]):
    def __init__(self):
        super().__init__(SensorReading)

    def get_latest_by_machine(self, db: Session, machine_id: int, limit: int = 10) -> List[SensorReading]:
        return db.query(SensorReading).filter(SensorReading.machine_id == machine_id).order_by(SensorReading.timestamp.desc()).limit(limit).all()

sensor_repository = SensorRepository()
