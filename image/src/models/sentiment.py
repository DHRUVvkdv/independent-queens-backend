from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class JournalEntry(BaseModel):
    """Request model for journal entry submission"""

    content: str
    user_id: str
    timestamp: datetime = datetime.utcnow()


class EmotionAnalysis(BaseModel):
    """Response model for emotion analysis"""

    emotions: Dict[str, float]
    dominant_emotion: str
    timestamp: datetime
    entry_id: str


class JournalAnalysisResponse(BaseModel):
    """Response model for journal analysis"""

    status: str
    analysis: EmotionAnalysis
