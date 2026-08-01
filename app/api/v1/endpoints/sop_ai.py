from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.ai.sop_retriever import SOPRetriever

router = APIRouter()

@router.get("/search", summary="Vector semantic search for SOPs & safety guidelines")
def search_sops(q: str, top_k: int = 3):
    return SOPRetriever.query_sops(q, top_k=top_k)
