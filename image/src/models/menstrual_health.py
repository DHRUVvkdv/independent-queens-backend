from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MenstrualPhase(str, Enum):
    MENSTRUAL = "menstrual"
    FOLLICULAR = "follicular"
    OVULATION = "ovulation"
    LUTEAL = "luteal"


class PhaseResponse(BaseModel):
    phase: Optional[MenstrualPhase] = None
    has_data: bool
    message: Optional[str] = None
    calculated_at: datetime = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "phase": "follicular",
                "has_data": True,
                "message": None,
                "calculated_at": "2024-02-02T12:00:00",
            }
        }
