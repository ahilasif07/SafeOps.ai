from typing import Tuple

class RiskMatrix:
    @staticmethod
    def get_risk_level(score: float) -> str:
        if score >= 65.0:
            return "CRITICAL"
        elif score >= 40.0:
            return "HIGH"
        elif score >= 20.0:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def evaluate_action(score: float) -> Tuple[str, bool]:
        """Returns (decision, is_blocked)"""
        if score >= 65.0:
            return ("BLOCKED", True)
        elif score >= 40.0:
            return ("SUPERVISOR_APPROVAL_REQUIRED", False)
        elif score >= 20.0:
            return ("PROCEED_WITH_CAUTION", False)
        else:
            return ("APPROVED", False)
