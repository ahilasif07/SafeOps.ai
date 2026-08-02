from typing import List, Optional, Protocol, Dict, Any
import difflib
import re

class DuplicateDetectorStrategy(Protocol):
    def calculate_similarity(
        self,
        new_title: str,
        new_description: str,
        new_machine_id: Optional[int],
        existing_title: str,
        existing_description: str,
        existing_machine_id: Optional[int],
    ) -> float:
        ...

class FuzzyStringDuplicateDetector:
    """
    Fuzzy String Similarity Engine.
    Combines title ratio, description token similarity, and machine matching.
    Can be seamlessly swapped with a Vector/Embedding Similarity Engine in the future.
    """

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        return " ".join(text.split())

    def calculate_similarity(
        self,
        new_title: str,
        new_description: str,
        new_machine_id: Optional[int],
        existing_title: str,
        existing_description: str,
        existing_machine_id: Optional[int],
    ) -> float:
        norm_new_title = self._normalize(new_title)
        norm_exist_title = self._normalize(existing_title)
        
        norm_new_desc = self._normalize(new_description)
        norm_exist_desc = self._normalize(existing_description)

        # Title similarity (Levenshtein sequence ratio) - Weight: 55%
        title_ratio = difflib.SequenceMatcher(None, norm_new_title, norm_exist_title).ratio()

        # Description similarity - Weight: 30%
        desc_ratio = difflib.SequenceMatcher(None, norm_new_desc, norm_exist_desc).ratio() if norm_new_desc and norm_exist_desc else 0.0

        # Machine match weight - Weight: 15%
        machine_match = 1.0 if (new_machine_id is not None and new_machine_id == existing_machine_id) else (0.5 if new_machine_id is None or existing_machine_id is None else 0.0)

        # Weighted composite score
        composite_score = (title_ratio * 0.55) + (desc_ratio * 0.30) + (machine_match * 0.15)
        return round(composite_score, 3)


class DuplicateDetectorEngine:
    def __init__(self, strategy: Optional[DuplicateDetectorStrategy] = None, default_threshold: float = 0.60):
        self.strategy = strategy or FuzzyStringDuplicateDetector()
        self.threshold = default_threshold

    def set_strategy(self, strategy: DuplicateDetectorStrategy):
        """Allows runtime substitution with Vector Embedding / Semantic Search Engine."""
        self.strategy = strategy

    def check_duplicate(
        self,
        new_title: str,
        new_description: str,
        new_machine_id: Optional[int],
        open_issues: List[Any],
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        target_threshold = threshold if threshold is not None else self.threshold
        duplicates = []

        for issue in open_issues:
            # Only compare open or in-progress issues
            if issue.status not in ["Open", "In Progress", "Waiting"]:
                continue

            score = self.strategy.calculate_similarity(
                new_title=new_title,
                new_description=new_description,
                new_machine_id=new_machine_id,
                existing_title=issue.title,
                existing_description=issue.description,
                existing_machine_id=issue.machine_id
            )

            if score >= target_threshold:
                duplicates.append({
                    "issue_id": issue.id,
                    "issue_code": issue.issue_code,
                    "title": issue.title,
                    "description": issue.description,
                    "machine_id": issue.machine_id,
                    "machine_name": issue.machine.name if issue.machine else "General Facility",
                    "status": issue.status,
                    "priority": issue.priority,
                    "created_at": issue.created_at.isoformat() if hasattr(issue.created_at, 'isoformat') else str(issue.created_at),
                    "similarity_score": score,
                    "similarity_percentage": int(score * 100)
                })

        duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)

        is_possible_duplicate = len(duplicates) > 0
        top_match = duplicates[0] if is_possible_duplicate else None

        return {
            "is_possible_duplicate": is_possible_duplicate,
            "threshold_used": target_threshold,
            "existing_issue_id": top_match["issue_id"] if top_match else None,
            "existing_issue_code": top_match["issue_code"] if top_match else None,
            "similarity_score": top_match["similarity_score"] if top_match else 0.0,
            "similarity_percentage": top_match["similarity_percentage"] if top_match else 0,
            "top_match": top_match,
            "all_matches": duplicates
        }

duplicate_engine = DuplicateDetectorEngine(default_threshold=0.55)
