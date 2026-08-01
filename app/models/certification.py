from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Certification(BaseModel):
    __tablename__ = "certifications"

    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)
    validity_months = Column(Integer, default=24, nullable=False)
    issuing_body = Column(String(100), default="OSHA Safety Institute")

    training_records = relationship("TrainingRecord", back_populates="certification", cascade="all, delete-orphan")

class TrainingRecord(BaseModel):
    __tablename__ = "training_records"

    worker_id = Column(Integer, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    certification_id = Column(Integer, ForeignKey("certifications.id", ondelete="CASCADE"), nullable=False)
    issued_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True, nullable=False)

    worker = relationship("Worker", back_populates="training_records")
    certification = relationship("Certification", back_populates="training_records")
