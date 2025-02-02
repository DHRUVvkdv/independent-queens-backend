from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Optional
from datetime import datetime
from uuid import uuid4


class EmotionAnalysis(BaseModel):
    """Model for emotion analysis results"""

    emotions: Dict[str, float]
    dominant_emotion: str
    timestamp: datetime
    entry_id: str = Field(default_factory=lambda: str(uuid4()))

    class Config:
        json_schema_extra = {
            "example": {
                "emotions": {
                    "neutral": 0.970521,
                    "approval": 0.012452,
                    "annoyance": 0.007191,
                },
                "dominant_emotion": "neutral",
                "timestamp": "2025-02-02T03:35:17.331704",
                "entry_id": "5a8742f6-a111-40c3-b7b7-17e0904960cb",
            }
        }


class Journal(BaseModel):
    """Model for journal entries"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr = Field(..., description="User's email - foreign key")
    title: str
    description: str
    date: str  # Format: MM-DD-YYYY
    bgColor: str
    emotion_analysis: Optional[EmotionAnalysis] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "9eae905a-5029-477a-a2a9-6cc933136a01",
                "email": "jane.doe@university.edu",
                "title": "Afternoon Thoughts",
                "description": "Making progress on the project, feeling optimistic...",
                "date": "01-02-2024",
                "bgColor": "bg-amber-100",
                "emotion_analysis": {
                    "emotions": {
                        "neutral": 0.970521,
                        "approval": 0.012452,
                        "annoyance": 0.007191,
                    },
                    "dominant_emotion": "neutral",
                    "timestamp": "2025-02-02T03:35:17.331704",
                    "entry_id": "5a8742f6-a111-40c3-b7b7-17e0904960cb",
                },
                "created_at": "2025-02-02T03:56:10.728000",
                "updated_at": "2025-02-02T03:56:10.728000",
            }
        }
