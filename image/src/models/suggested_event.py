from pydantic import BaseModel
from datetime import datetime
from typing import List


class SuggestedEvent(BaseModel):
    id: str
    title: str
    start: str
    end: str
    color: str
    type: str  # Type of activity (e.g., "wellness", "productivity")
    reason: str  # Reason for suggestion

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sugg_123e4567-e89b-12d3-a456-426614174000",
                "title": "Light Evening Walk",
                "start": "2024-05-11 17:00",
                "end": "2024-05-11 17:30",
                "color": "#4CAF50",  # Green for wellness activities
                "type": "wellness",
                "reason": "Light exercise recommended during menstrual phase",
            }
        }


# Color mapping for different event types
EVENT_COLORS = {
    "wellness": "#4CAF50",  # Green
    "productivity": "#2196F3",  # Blue
    "rest": "#9C27B0",  # Purple
    "social": "#FF9800",  # Orange
    "learning": "#795548",  # Brown
}
