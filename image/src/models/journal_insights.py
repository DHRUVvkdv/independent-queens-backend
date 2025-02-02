from pydantic import BaseModel, Field
from typing import Dict, List
from datetime import datetime


class DateRange(BaseModel):
    start: str  # Format: MM-DD-YYYY
    end: str  # Format: MM-DD-YYYY


class InsightsMetadata(BaseModel):
    date_range: DateRange
    total_entries: int


class EmotionStats(BaseModel):
    count: int
    average_score: float


class EmotionCountWithScore(BaseModel):
    emotion: str
    count: int
    average_score: float


class EmotionCount(BaseModel):
    emotion: str
    count: int


class EmotionCounts(BaseModel):
    all_emotions: Dict[str, EmotionStats]
    dominant_emotions: Dict[str, int]


class SortedEmotionCounts(BaseModel):
    all_emotions: List[EmotionCountWithScore]
    dominant_emotions: List[EmotionCount]


class JournalInsights(BaseModel):
    metadata: InsightsMetadata
    emotions: EmotionCounts
    sorted_emotions: SortedEmotionCounts

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "date_range": {"start": "01-02-2024", "end": "02-02-2024"},
                    "total_entries": 15,
                },
                "emotions": {
                    "all_emotions": {
                        "joy": {"count": 25, "average_score": 0.8523},
                        "neutral": {"count": 20, "average_score": 0.7234},
                        "optimism": {"count": 15, "average_score": 0.6532},
                    },
                    "dominant_emotions": {"joy": 5, "neutral": 4, "optimism": 3},
                },
                "sorted_emotions": {
                    "all_emotions": [
                        {"emotion": "joy", "count": 25, "average_score": 0.8523},
                        {"emotion": "neutral", "count": 20, "average_score": 0.7234},
                        {"emotion": "optimism", "count": 15, "average_score": 0.6532},
                    ],
                    "dominant_emotions": [
                        {"emotion": "joy", "count": 5},
                        {"emotion": "neutral", "count": 4},
                        {"emotion": "optimism", "count": 3},
                    ],
                },
            }
        }
