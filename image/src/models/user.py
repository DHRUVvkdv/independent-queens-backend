from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class Assignment(BaseModel):
    date_due: str
    time_due: str
    name: str
    canvas_link: str


class Event(BaseModel):
    id: str  # Changed from UUID to str to avoid MongoDB UUID issues
    title: str
    start: str
    end: str
    color: str


class QAPair(BaseModel):
    question: str
    answer: str


class User(BaseModel):
    email: EmailStr = Field(..., description="User's email - primary identifier")
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    canvas_token: Optional[str] = None
    coins: int = Field(default=0, ge=0)
    profile_image_path: Optional[str] = None
    bio: Optional[str] = None
    profession: Optional[str] = None
    university: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    assignments: List[Assignment] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    qa_pairs: List[QAPair] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jane.doe@university.edu",
                "first_name": "Jane",
                "last_name": "Doe",
                "phone_number": "+1234567890",
                "canvas_token": "canvas_token_xxx",
                "coins": 100,
                "profile_image_path": "users/profile/xxx.jpg",
                "bio": "Computer Science student",
                "profession": "Student",
                "university": "MIT",
                "age": 22,
                "skills": ["Python", "AWS"],
                "interests": ["AI", "Cloud Computing"],
                "location": "Boston, MA",
            }
        }
