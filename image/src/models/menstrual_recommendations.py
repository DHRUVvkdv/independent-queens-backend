from pydantic import BaseModel
from typing import List
from datetime import datetime
from models.menstrual_health import MenstrualPhase


class MenstrualRecommendations(BaseModel):
    phase: MenstrualPhase
    diet_recommendations: List[str]
    exercise_recommendations: List[str]
    symptoms_to_watch: List[str]
    affirmation: str
    generated_at: datetime = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "phase": "follicular",
                "diet_recommendations": [
                    "Increase iron intake through leafy greens",
                    "Consume vitamin C rich fruits",
                    "Include lean proteins",
                    "Stay hydrated with herbal teas",
                    "Add whole grains",
                    "Consider magnesium-rich foods",
                ],
                "exercise_recommendations": [
                    "Light walking for 20 minutes",
                    "Gentle yoga stretches",
                    "Swimming if comfortable",
                    "Light resistance training",
                    "Balance exercises",
                    "Deep breathing exercises",
                ],
                "symptoms_to_watch": [
                    "Mild cramping",
                    "Light spotting",
                    "Changes in energy levels",
                    "Breast tenderness",
                    "Mood fluctuations",
                    "Sleep pattern changes",
                ],
                "affirmation": "I am in tune with my body's natural rhythm",
                "generated_at": "2024-02-02T12:00:00",
            }
        }
