from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, workers, machines, procedures, tasks,
    certifications, incidents, supervisor_approvals,
    sensor_readings, safety_eval, sop_ai
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(workers.router, prefix="/workers", tags=["Workers & Credentials"])
api_router.include_router(machines.router, prefix="/machines", tags=["Industrial Machinery"])
api_router.include_router(procedures.router, prefix="/procedures", tags=["Standard Operating Procedures (SOPs)"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Maintenance Work Orders"])
api_router.include_router(certifications.router, prefix="/certifications", tags=["Safety Certifications"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents & Near Misses"])
api_router.include_router(supervisor_approvals.router, prefix="/approvals", tags=["Supervisor Sign-offs"])
api_router.include_router(sensor_readings.router, prefix="/sensors", tags=["IoT Telemetry"])
api_router.include_router(safety_eval.router, prefix="/safety", tags=["Risk Engine & Safety Evaluation"])
api_router.include_router(sop_ai.router, prefix="/sop-ai", tags=["AI Copilot & Vector SOP Search"])
