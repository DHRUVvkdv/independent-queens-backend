from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class OfferCreate(BaseModel):
    """Request model for creating an offer"""

    email: EmailStr
    title: str = Field(..., min_length=1, max_length=100)
    detail: str = Field(..., min_length=1, max_length=1000)
    skill: str = Field(..., min_length=1, max_length=50)
    pointCost: int = Field(..., gt=0)
    duration: int = Field(..., gt=0)  # Duration in days


class OfferResponse(BaseModel):
    """Response model for offer"""

    id: str  # Using string for UUID
    email: EmailStr
    title: str
    detail: str
    skill: str
    pointCost: int
    duration: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class OfferUpdate(BaseModel):
    """Request model for updating an offer"""

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    detail: Optional[str] = Field(None, min_length=1, max_length=1000)
    skill: Optional[str] = Field(None, min_length=1, max_length=50)
    pointCost: Optional[int] = Field(None, gt=0)
    duration: Optional[int] = Field(None, gt=0)
