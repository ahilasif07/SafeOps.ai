import datetime
from sqlalchemy.orm import Session
from app.database.session import engine, SessionLocal
from app.models.base import Base
from app.models.worker import Worker
from app.models.machine import Machine
from app.models.procedure import Procedure, ProcedureStep
from app.models.certification import Certification, TrainingRecord
from app.models.incident import Incident
from app.models.sensor import SensorReading
from app.models.supervisor import SupervisorApproval
from app.models.task import Task
from app.auth.security import get_password_hash
from app.ai.sop_retriever import SOPRetriever
from app.utils.logger import logger

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Worker).first():
        logger.info("Database already seeded.")
        db.close()
        return

    logger.info("Seeding initial SafeOps AI industrial dataset...")

    # 1. Certifications
    cert_elec = Certification(code="CERT-ELEC-01", name="High-Voltage Electrical Safety", validity_months=24, issuing_body="OSHA Safety Board")
    cert_loto = Certification(code="CERT-LOTO-01", name="Lock-Out / Tag-Out Authorized Specialist", validity_months=12, issuing_body="National Safety Council")
    cert_hazmat = Certification(code="CERT-HAZMAT-01", name="Hazmat & Chemical Handling", validity_months=24, issuing_body="EPA Industrial Safety")
    cert_hyd = Certification(code="CERT-HYD-01", name="High-Pressure Hydraulics", validity_months=36, issuing_body="Fluid Power Society")

    db.add_all([cert_elec, cert_loto, cert_hazmat, cert_hyd])
    db.commit()

    # 2. Workers
    pass_hash = get_password_hash("SafeOpsPass2026!")
    w1 = Worker(worker_code="WRK-1001", full_name="John Doe", email="john.doe@safeops.io", role="TECHNICIAN", department="ELECTRICAL", clearance_level=3, is_active=True, hashed_password=pass_hash)
    w2 = Worker(worker_code="WRK-1002", full_name="Sarah Connor", email="sarah.c@safeops.io", role="SUPERVISOR", department="PLANT_OPS", clearance_level=5, is_active=True, hashed_password=pass_hash)
    w3 = Worker(worker_code="WRK-1003", full_name="Mike Vance", email="mike.vance@safeops.io", role="TECHNICIAN", department="MECHANICAL", clearance_level=1, is_active=True, hashed_password=pass_hash)
    w4 = Worker(worker_code="WRK-1004", full_name="Alex Mercer", email="alex.m@safeops.io", role="SAFETY_OFFICER", department="SAFETY_DEPT", clearance_level=4, is_active=True, hashed_password=pass_hash)

    db.add_all([w1, w2, w3, w4])
    db.commit()

    # 3. Training Records
    now = datetime.datetime.utcnow()
    tr1 = TrainingRecord(worker_id=w1.id, certification_id=cert_elec.id, issued_date=now - datetime.timedelta(days=100), expiry_date=now + datetime.timedelta(days=600), is_valid=True)
    tr2 = TrainingRecord(worker_id=w1.id, certification_id=cert_loto.id, issued_date=now - datetime.timedelta(days=50), expiry_date=now + datetime.timedelta(days=300), is_valid=True)
    tr3 = TrainingRecord(worker_id=w3.id, certification_id=cert_loto.id, issued_date=now - datetime.timedelta(days=400), expiry_date=now - datetime.timedelta(days=35), is_valid=False) # Expired!

    db.add_all([tr1, tr2, tr3])
    db.commit()

    # 4. Machines
    m1 = Machine(machine_code="MCH-TURB-01", name="Main Gas Turbine Alpha", model="Siemens SGT-800", location="Sector A - Powerhouse", status="OPERATIONAL", safety_rating=92.5, requires_loto=True)
    m2 = Machine(machine_code="MCH-PRESS-04", name="Hydraulic Stamping Press 4", model="Schuler 1000T", location="Sector B - Fabrication", status="MAINTENANCE", safety_rating=84.0, requires_loto=True)
    m3 = Machine(machine_code="MCH-CHEM-02", name="Chemical Reactor Vessel 2", model="Pfaudler 5000L", location="Sector C - Chemical Processing", status="HAZARDOUS", safety_rating=65.0, requires_loto=True)

    db.add_all([m1, m2, m3])
    db.commit()

    # 5. Procedures & Steps
    p1 = Procedure(procedure_code="SOP-ELEC-401", title="High-Voltage Transformer Maintenance & Inspection", description="Standard procedure for isolating, testing, and replacing transformer coils.", category="ELECTRICAL", required_clearance_level=3, is_approved=True, version="2.1")
    db.add(p1)
    db.commit()

    s1_1 = ProcedureStep(procedure_id=p1.id, step_number=1, title="Verify Lock-Out / Tag-Out (LOTO)", instruction="De-energize main 13.8kV circuit breaker and place master padlocks.", hazard_level="CRITICAL", requires_supervisor_signoff=True, required_ppe="Arc Flash Suit Level 4, Insulated Gloves 20kV")
    s1_2 = ProcedureStep(procedure_id=p1.id, step_number=2, title="Grounding Rod Discharge", instruction="Attach grounding cable to discharge remaining capacitive charge.", hazard_level="HIGH", requires_supervisor_signoff=False, required_ppe="Safety Glasses, Insulated Gloves 20kV")
    s1_3 = ProcedureStep(procedure_id=p1.id, step_number=3, title="Insulation Oil Sampling", instruction="Extract 500ml of oil from the bottom valve for breakdown voltage testing.", hazard_level="MEDIUM", requires_supervisor_signoff=False, required_ppe="Nitrile Gloves, Respirator")

    p2 = Procedure(procedure_code="SOP-HYD-202", title="Hydraulic Cylinder Seal Replacement", description="Procedure for depressurizing and replacing piston rod seals on stamping presses.", category="HYDRAULIC", required_clearance_level=2, is_approved=True, version="1.0")
    db.add(p2)
    db.commit()

    s2_1 = ProcedureStep(procedure_id=p2.id, step_number=1, title="Bleed Hydraulic Line Pressure", instruction="Open bleed valve V-102 until accumulator pressure reads 0 PSI.", hazard_level="HIGH", requires_supervisor_signoff=True, required_ppe="Face Shield, Heavy Leather Gloves")
    s2_2 = ProcedureStep(procedure_id=p2.id, step_number=2, title="Remove Cylinder End Cap", instruction="Unbolt 12 M24 retaining bolts in star pattern.", hazard_level="MEDIUM", requires_supervisor_signoff=False, required_ppe="Steel Toe Boots, Safety Glasses")

    db.add_all([s1_1, s1_2, s1_3, s2_1, s2_2])
    db.commit()

    # Index procedures in vector retriever
    SOPRetriever.index_procedure(p1.id, p1.procedure_code, p1.title, p1.description, p1.category, [s1_1, s1_2, s1_3])
    SOPRetriever.index_procedure(p2.id, p2.procedure_code, p2.title, p2.description, p2.category, [s2_1, s2_2])

    # 6. Sensor Readings
    sr1 = SensorReading(machine_id=m1.id, sensor_type="TEMPERATURE", value=68.5, unit="C", is_anomaly=False, timestamp=now)
    sr2 = SensorReading(machine_id=m1.id, sensor_type="VIBRATION", value=2.1, unit="mm/s", is_anomaly=False, timestamp=now)
    sr3 = SensorReading(machine_id=m3.id, sensor_type="TOXIC_GAS", value=18.4, unit="ppm", is_anomaly=True, timestamp=now)
    sr4 = SensorReading(machine_id=m3.id, sensor_type="TEMPERATURE", value=102.3, unit="C", is_anomaly=True, timestamp=now)

    db.add_all([sr1, sr2, sr3, sr4])
    db.commit()

    # 7. Incidents
    inc1 = Incident(incident_code="INC-2026-001", title="Over-pressurization Alarm on Reactor 2", description="Pressure spiked to 145 PSI during chemical batching process.", severity="HIGH", machine_id=m3.id, reported_at=now - datetime.timedelta(days=5), resolution_status="UNDER_INVESTIGATION")
    db.add(inc1)
    db.commit()

    db.close()
    logger.info("SafeOps AI Database initialization & seeding completed successfully.")
