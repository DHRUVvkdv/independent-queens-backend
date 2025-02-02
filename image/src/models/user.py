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
    cognito_id: str = Field(..., description="AWS Cognito User ID")
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
                "cognito_id": "us-east-1_xxxxxx_123e4567-e89b-12d3-a456-426614174000",
                "first_name": "Jane",
                "last_name": "Doe",
                "phone_number": "+1234567890",
                "canvas_token": "canvas_token_xyz_123",
                "coins": 10,
                "profile_image_path": "users/profiles/jane_doe_123.jpg",
                "bio": "Computer Science graduate student passionate about AI and cloud computing",
                "profession": "Graduate Student",
                "university": "MIT",
                "age": 24,
                "skills": [
                    "Python",
                    "AWS",
                    "Machine Learning",
                    "Data Structures",
                    "Algorithms",
                ],
                "interests": [
                    "Artificial Intelligence",
                    "Cloud Computing",
                    "Women in Tech",
                    "Research",
                    "Hackathons",
                ],
                "location": "Cambridge, MA",
            }
        }


class SignUpUser(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    age: int = Field(..., ge=0, le=120)
    profession: str
    skills: List[str]
    interests: Optional[List[str]] = []
    university: str


class SignInUser(BaseModel):
    email: EmailStr
    password: str
