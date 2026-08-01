from typing import List
from sqlalchemy.orm import Session
from app.repositories.sensor_repository import sensor_repository
from app.schemas.sensor import SensorReadingCreate, SensorReadingOut
from app.sensor_simulator.telemetry import telemetry_simulator
from app.models.sensor import SensorReading

class SensorService:
    def log_reading(self, db: Session, reading_in: SensorReadingCreate) -> SensorReading:
        data = reading_in.dict()
        # Anomaly threshold check
        val = data["value"]
        st = data["sensor_type"]
        is_anomaly = (st == "TEMPERATURE" and val > 90.0) or (st == "PRESSURE" and val > 130.0) or (st == "VIBRATION" and val > 7.0) or (st == "TOXIC_GAS" and val > 10.0)
        data["is_anomaly"] = is_anomaly
        return sensor_repository.create(db, data)

    def get_latest_readings(self, db: Session, machine_id: int, limit: int = 10) -> List[SensorReading]:
        return sensor_repository.get_latest_by_machine(db, machine_id, limit)

    def trigger_telemetry_simulation(self, db: Session, machine_id: int, force_anomaly: bool = False) -> List[SensorReadingOut]:
        return telemetry_simulator.simulate_machine_readings(db, machine_id, force_anomaly)

sensor_service = SensorService()
