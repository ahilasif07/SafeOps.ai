import os
from google import genai
from app.utils.config import settings
from app.utils.logger import logger

class GeminiSafetyAdvisor:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    def generate_safety_briefing(self, worker_name: str, machine_name: str, procedure_title: str, risk_score: float, risk_level: str, hazards: list) -> str:
        if not self.client:
            # Fallback high-quality structured safety advisory when API key is missing/unconfigured
            return (
                f"⚠️ [SafeOps AI Safety Briefing for {worker_name}]\n"
                f"Task: {procedure_title} on {machine_name}\n"
                f"Evaluated Risk Score: {risk_score}/100 ({risk_level})\n\n"
                f"Critical Directives:\n"
                f"1. Perform mandatory LOTO verification prior to touching circuit conductors or hydraulic lines.\n"
                f"2. Mandatory PPE: Arc Flash Level 4, Insulated Gloves (20kV), Steel Toe Boots.\n"
                f"3. Ensure secondary supervisor signoff is logged before initiating hazardous steps.\n"
                f"Identify hazards: {', '.join(hazards) if hazards else 'None detected.'}"
            )

        prompt = (
            f"You are SafeOps AI, an industrial safety copilot. Generate a concise, urgent 3-bullet point safety briefing "
            f"for technician {worker_name} executing '{procedure_title}' on '{machine_name}'. "
            f"Risk Score: {risk_score}/100 ({risk_level}). Identified hazard factors: {hazards}. "
            f"Include required PPE and lock-out tag-out instructions."
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error invoking Gemini API: {e}")
            return f"SafeOps AI Advisory: Risk level is {risk_level} ({risk_score}/100). Maintain full PPE compliance and supervisor signoff."

gemini_advisor = GeminiSafetyAdvisor()
