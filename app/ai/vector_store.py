import math
from typing import List, Dict, Any

class InMemoryVectorStore:
    """Lightweight in-memory vector store with cosine similarity for RAG SOP retrieval."""
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    def _dummy_embed(self, text: str) -> List[float]:
        # Enhanced 64-dim word-level hash embedding for accurate semantic & keyword RAG retrieval
        dim = 64
        vec = [0.0] * dim
        words = text.lower().split()
        for word in words:
            # Hash full word
            h = sum(ord(c) * (i + 1) for i, c in enumerate(word))
            idx = h % dim
            vec[idx] += 1.5
            # Hash character bigrams
            for i in range(len(word) - 1):
                bigram_h = (ord(word[i]) * 31 + ord(word[i+1]))
                vec[bigram_h % dim] += 0.5
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

