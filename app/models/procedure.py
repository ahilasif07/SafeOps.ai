from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

machine_sop_association = Table(
    "machine_sop_association",
    BaseModel.metadata,
    Column("machine_id", Integer, ForeignKey("machines.id", ondelete="CASCADE"), primary_key=True),
    Column("procedure_id", Integer, ForeignKey("procedures.id", ondelete="CASCADE"), primary_key=True)
)

class Procedure(BaseModel):
    __tablename__ = "procedures"

    procedure_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="ELECTRICAL") # ELECTRICAL, MECHANICAL, CHEMICAL, HYDRAULIC
    required_clearance_level = Column(Integer, default=1, nullable=False)
    is_approved = Column(Boolean, default=True, nullable=False)
    version = Column(String(20), default="1.0", nullable=False)

    steps = relationship("ProcedureStep", back_populates="procedure", cascade="all, delete-orphan", order_by="ProcedureStep.step_number")
    tasks = relationship("Task", back_populates="procedure")
    machines = relationship("Machine", secondary=machine_sop_association, back_populates="sops")

class ProcedureStep(BaseModel):
    __tablename__ = "procedure_steps"

    procedure_id = Column(Integer, ForeignKey("procedures.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Integer, nullable=False)
    title = Column(String(150), nullable=False)
    instruction = Column(Text, nullable=False)
    hazard_level = Column(String(20), default="LOW", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    requires_supervisor_signoff = Column(Boolean, default=False)
    required_ppe = Column(String(200), default="Safety Glasses, Steel Toe Boots")

    procedure = relationship("Procedure", back_populates="steps")
