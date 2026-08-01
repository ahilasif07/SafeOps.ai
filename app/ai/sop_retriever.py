from typing import List, Dict, Any
from app.ai.vector_store import vector_store

class SOPRetriever:
    @staticmethod
    def index_procedure(procedure_id: int, code: str, title: str, description: str, category: str, steps: List[Any]):
        step_text = "\n".join([f"Step {s.step_number}: {s.title} - {s.instruction} (Hazard: {s.hazard_level}, PPE: {s.required_ppe})" for s in steps])
        full_content = f"SOP Code: {code}\nTitle: {title}\nCategory: {category}\nDescription: {description}\nSteps:\n{step_text}"

        vector_store.add_document(
            doc_id=f"SOP-{procedure_id}",
            content=full_content,
            metadata={
                "procedure_id": procedure_id,
                "code": code,
                "title": title,
                "category": category
            }
        )

    @staticmethod
    def query_sops(query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return vector_store.search(query_text, top_k=top_k)

sop_retriever = SOPRetriever()
