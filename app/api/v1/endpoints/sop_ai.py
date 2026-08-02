from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.session import get_db
from app.ai.sop_retriever import SOPRetriever
from app.services.procedure_service import procedure_service

router = APIRouter()

@router.get("/search", summary="Vector semantic search for SOPs & safety guidelines")
def search_sops(q: str, top_k: int = 3, db: Session = Depends(get_db)):
    raw_results = SOPRetriever.query_sops(q, top_k=top_k, db=db)
    formatted = []
    for r in raw_results:
        meta = r.get("metadata", {})
        formatted.append({
            "id": r.get("id"),
            "procedure_id": meta.get("procedure_id"),
            "code": meta.get("code") or meta.get("procedure_code"),
            "title": meta.get("title"),
            "category": meta.get("category"),
            "description": meta.get("description") or (r.get("content", "").split("\n")[3] if len(r.get("content", "").split("\n")) > 3 else r.get("content", "")[:150]),
            "content": r.get("content"),
            "score": r.get("score", 0.0),
            "similarity_score": r.get("score", 0.0)
        })
    return formatted

@router.post("/reindex", summary="Reindex all published SOPs into Vector Store")
def reindex_all_sops(db: Session = Depends(get_db)):
    count = SOPRetriever.sync_all_from_db(db)
    return {"status": "success", "indexed_count": count, "message": f"Successfully vector-indexed {count} SOPs"}

@router.post("/index/{procedure_id}", summary="Index or reindex single SOP into Vector Store")
def index_single_sop(procedure_id: int, db: Session = Depends(get_db)):
    proc = procedure_service.get_procedure(db, procedure_id)
    if not proc:
        return {"status": "error", "message": "SOP not found"}
    SOPRetriever.index_procedure(proc.id, proc.procedure_code, proc.title, proc.description or "", proc.category, proc.steps or [])
    return {"status": "success", "procedure_id": proc.id, "message": f"Vector indexed SOP {proc.procedure_code}"}


