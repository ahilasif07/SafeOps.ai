import math
from typing import List, Dict, Any

class InMemoryVectorStore:
    """Lightweight in-memory vector store with cosine similarity for RAG SOP retrieval."""
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    def _dummy_embed(self, text: str) -> List[float]:
        # Simple deterministic hash vector for text similarity without external heavy DL dependencies
        vec = [0.0] * 32
        for i, char in enumerate(text.lower()):
            vec[ord(char) % 32] += 1.0
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        self.documents = [d for d in self.documents if d["id"] != doc_id]
        embedding = self._dummy_embed(content)
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata,
            "embedding": embedding
        })

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
        q_vec = self._dummy_embed(query)

        scored = []
        for doc in self.documents:
            d_vec = doc["embedding"]
            similarity = sum(a * b for a, b in zip(q_vec, d_vec))
            scored.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": round(similarity, 4)
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

vector_store = InMemoryVectorStore()
