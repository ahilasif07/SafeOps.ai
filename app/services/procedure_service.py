import io
import re
import random
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from pypdf import PdfReader
from app.repositories.procedure_repository import procedure_repository
from app.schemas.procedure import ProcedureCreate, ProcedureUpdate
from app.models.procedure import Procedure, ProcedureStep
from app.ai.sop_retriever import SOPRetriever
from app.utils.logger import logger

class ProcedureService:
    def get_procedures(self, db: Session, skip: int = 0, limit: int = 100) -> List[Procedure]:
        return procedure_repository.get_all(db, skip=skip, limit=limit)

    def get_procedure(self, db: Session, proc_id: int) -> Optional[Procedure]:
        return procedure_repository.get(db, proc_id)

    def create_procedure(self, db: Session, proc_in: ProcedureCreate) -> Procedure:
        data = proc_in.dict()
        steps_data = data.pop("steps", [])

        proc = procedure_repository.create(db, data)
        steps_objs = []
        for step in steps_data:
            s_obj = ProcedureStep(procedure_id=proc.id, **step)
            db.add(s_obj)
            steps_objs.append(s_obj)
        db.commit()
        db.refresh(proc)

        # Index into vector retriever
        SOPRetriever.index_procedure(proc.id, proc.procedure_code, proc.title, proc.description or "", proc.category, steps_objs)

        return proc

    def update_procedure(self, db: Session, proc_id: int, proc_in: ProcedureCreate) -> Optional[Procedure]:
        proc = procedure_repository.get(db, proc_id)
        if not proc:
            return None
        data = proc_in.dict()
        steps_data = data.pop("steps", [])

        # Update base procedure attributes
        proc = procedure_repository.update(db, proc, data)

        # Replace existing steps
        db.query(ProcedureStep).filter(ProcedureStep.procedure_id == proc.id).delete()
        steps_objs = []
        for step in steps_data:
            s_obj = ProcedureStep(procedure_id=proc.id, **step)
            db.add(s_obj)
            steps_objs.append(s_obj)
        db.commit()
        db.refresh(proc)

        # Re-index into vector retriever
        SOPRetriever.index_procedure(proc.id, proc.procedure_code, proc.title, proc.description or "", proc.category, steps_objs)

        return proc

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
            return "\n\n".join(text_pages).strip()
        except Exception as e:
            logger.error(f"Error reading PDF bytes: {e}")
            return ""

    def parse_pdf_and_create_sop(self, db: Session, pdf_bytes: bytes, filename: str) -> Procedure:
        text = self.extract_text_from_pdf(pdf_bytes)
        code_suffix = str(random.randint(100, 999))
        clean_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")

        title = clean_name.title()
        description = "Uploaded SOP Document"
        category = "MECHANICAL"
        if "elec" in clean_name.lower():
            category = "ELECTRICAL"
        elif "chem" in clean_name.lower():
            category = "CHEMICAL"
        elif "hyd" in clean_name.lower():
            category = "HYDRAULIC"

        steps = []
        if text:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if lines:
                title = lines[0][:100]
                if len(lines) > 1:
                    description = " ".join(lines[1:4])[:250]

            step_num = 1
            for line in lines:
                if re.match(r"^(step|\d+[\.\)]|\-|\*)\s*", line, re.IGNORECASE) or len(line) > 15:
                    hazard = "LOW"
                    l_lower = line.lower()
                    if any(w in l_lower for w in ["danger", "critical", "high", "loto", "voltage"]):
                        hazard = "HIGH"
                    elif any(w in l_lower for w in ["caution", "warn", "medium"]):
                        hazard = "MEDIUM"
                    
                    steps.append({
                        "step_number": step_num,
                        "title": line[:40].strip(" -:."),
                        "instruction": line,
                        "hazard_level": hazard,
                        "requires_supervisor_signoff": hazard == "HIGH",
                        "required_ppe": "Safety Glasses, Steel Toe Boots" + (", Insulated Gloves" if hazard == "HIGH" else "")
                    })
                    step_num += 1

        if not steps:
            steps = [
                {
                    "step_number": 1,
                    "title": "Document Inspection",
                    "instruction": f"Review imported document '{filename}' requirements and verify environmental safety checks.",
                    "hazard_level": "LOW",
                    "requires_supervisor_signoff": False,
                    "required_ppe": "Standard PPE"
                }
            ]

        proc_in = ProcedureCreate(
            procedure_code=f"SOP-PDF-{code_suffix}",
            title=title or f"Imported SOP: {clean_name}",
            description=description or f"Parsed from {filename}",
            category=category,
            required_clearance_level=2 if category in ["ELECTRICAL", "CHEMICAL"] else 1,
            is_approved=True,
            version="1.0",
            steps=steps
        )
        return self.create_procedure(db, proc_in)

procedure_service = ProcedureService()
