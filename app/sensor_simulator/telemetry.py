from typing import List
from sqlalchemy.orm import Session
from app.sensor_simulator.generator import SensorGenerator
from app.repositories.sensor_repository import sensor_repository
from app.schemas.sensor import SensorReadingOut

class TelemetrySimulator:
    @staticmethod
    def simulate_machine_readings(db: Session, machine_id: int, force_anomaly: bool = False) -> List[SensorReadingOut]:
        sensor_types = ["TEMPERATURE", "PRESSURE", "VIBRATION"]
        if machine_id % 2 == 1:
            sensor_types.append("TOXIC_GAS")

        results = []
        for st in sensor_types:
            data = SensorGenerator.generate_reading(st, force_anomaly=force_anomaly)
            data["machine_id"] = machine_id
            reading = sensor_repository.create(db, data)
            results.append(SensorReadingOut.from_orm(reading))
        return results

telemetry_simulator = TelemetrySimulator()
