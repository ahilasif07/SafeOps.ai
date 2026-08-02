from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.ai.vector_store import vector_store

class SOPRetriever:
    @staticmethod
    def index_procedure(procedure_id: int, code: str, title: str, description: str, category: str, steps: List[Any]):
        step_lines = []
        for s in steps:
            s_num = getattr(s, 'step_number', None) or (s.get('step_number') if isinstance(s, dict) else 1)
            s_title = getattr(s, 'title', None) or (s.get('title') if isinstance(s, dict) else '') or ''
            s_inst = getattr(s, 'instruction', None) or (s.get('instruction') if isinstance(s, dict) else '') or ''
            s_haz = getattr(s, 'hazard_level', None) or (s.get('hazard_level') if isinstance(s, dict) else 'LOW') or 'LOW'
            s_ppe = getattr(s, 'required_ppe', None) or (s.get('required_ppe') if isinstance(s, dict) else '') or ''
            step_lines.append(f"Step {s_num}: {s_title} - {s_inst} (Hazard: {s_haz}, PPE: {s_ppe})")

        step_text = "\n".join(step_lines)
        full_content = f"SOP Code: {code}\nTitle: {title}\nCategory: {category}\nDescription: {description or ''}\nSteps:\n{step_text}"

        vector_store.add_document(
            doc_id=f"SOP-{procedure_id}",
            content=full_content,
            metadata={
                "procedure_id": procedure_id,
                "code": code,
                "title": title,
                "category": category,
                "indexed": True
            }
        )

    @classmethod
    def sync_all_from_db(cls, db: Session) -> int:
        from app.models.procedure import Procedure
        procs = db.query(Procedure).all()
        for p in procs:
            cls.index_procedure(p.id, p.procedure_code, p.title, p.description or "", p.category, p.steps or [])
        return len(procs)

    @classmethod
    def query_sops(cls, query_text: str, top_k: int = 3, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        if db is not None and len(vector_store.documents) == 0:
            cls.sync_all_from_db(db)
        return vector_store.search(query_text, top_k=top_k)

sop_retriever = SOPRetriever()

