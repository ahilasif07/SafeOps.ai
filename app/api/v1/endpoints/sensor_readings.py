from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.sensor import SensorReadingOut, SensorReadingCreate
from app.services.sensor_service import sensor_service

router = APIRouter()

@router.post("/log", response_model=SensorReadingOut, summary="Log sensor reading from machine IoT gateway")
def log_reading(reading_in: SensorReadingCreate, db: Session = Depends(get_db)):
    return sensor_service.log_reading(db, reading_in)

@router.get("/machine/{machine_id}", response_model=List[SensorReadingOut], summary="Get latest telemetry readings for a machine")
def get_machine_telemetry(machine_id: int, limit: int = 10, db: Session = Depends(get_db)):
    return sensor_service.get_latest_readings(db, machine_id, limit)

@router.post("/simulate/{machine_id}", response_model=List[SensorReadingOut], summary="Trigger IoT telemetry simulation for machine")
def simulate_telemetry(machine_id: int, force_anomaly: bool = False, db: Session = Depends(get_db)):
    return sensor_service.trigger_telemetry_simulation(db, machine_id, force_anomaly)
