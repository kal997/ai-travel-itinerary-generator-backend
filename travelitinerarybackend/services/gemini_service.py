import json
from functools import lru_cache
from typing import List

import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

from travelitinerarybackend.config import config

# Initialize Vertex AI SDK
vertexai.init(project=config.GCP_PROJECT_ID, location=config.GCP_REGION)


class GeminiService:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-flash")

    def generate_itinerary(
        self, destination: str, start_date: str, end_date: str, interests: List[str]
    ) -> List[dict]:
        prompt = f"""
You are a travel assistant. Based on the user input below, generate a JSON itinerary.

User input:
{{
  "destination": "{destination}",
  "start_date": "{start_date}",
  "end_date": "{end_date}",
  "interests": {interests}
}}

Respond ONLY with a valid JSON object like:
{{
  "itinerary": [
    {{
      "day": 1,
      "activities": ["Visit the Eiffel Tower", "Lunch at a bistro", "Evening Seine river cruise"]
    }}
  ]
}}
"""

        try:
            response = self.model.generate_content([Part.from_text(prompt)])
            raw_text = response.candidates[0].content.parts[0].text
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_text)
            return parsed.get("itinerary", [])
        except Exception as e:
            raise RuntimeError(f"Failed to parse Gemini Vertex response: {e}")


@lru_cache()
def get_gemini_service() -> GeminiService:
    return GeminiService()
