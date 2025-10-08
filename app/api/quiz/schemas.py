from pydantic import BaseModel, UUID4, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID

class ProfileBase(BaseModel):
    name: str = Field(..., example="John Doe", description="Full name of the user")
    age: int = Field(..., gt=0, lt=120, example=30, description="Age of the user")
    gender: str = Field(..., example="Male", description="Gender of the user")
    education: str = Field(..., example="Bachelor's in Computer Science", description="Highest education level")
    city: str = Field(..., example="New York", description="City of residence")
    hobbies: List[str] = Field(..., example=["reading", "gaming", "cycling"], description="List of hobbies")
    bio: Optional[str] = Field(None, example="A software engineer who loves hiking and coffee.", description="Short bio")

class ProfileCreate(ProfileBase):
    """
    Schema for profile creation.
    Inherits all fields from ProfileBase.
    """
    pass

class ProfileResponse(ProfileBase):
    id: UUID
    user_id: UUID = Field(..., description="ID of the associated user")

    class Config:
        from_attributes = True 


# Reused by both input/output
class QuizQuestion(BaseModel):
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None

class QuizGenerateResponse(BaseModel):
    quiz_id: UUID4
    total_questions: int
    questions: List[QuizQuestion]

# Optional: If you want to expose quiz metadata
class QuizMetadata(BaseModel):
    source: Optional[str]
    model: Optional[str]

class QuizResponseFull(BaseModel):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    total_questions: int
    quiz_type: str
    tags: List[str]
    metadata: Optional[QuizMetadata]
    profile_snapshot: dict
    questions: List[QuizQuestion]

    class Config:
        from_attributes = True


class QuizAnswerSubmission(BaseModel):
    question_id: UUID4
    answer_text: str
    is_correct: Optional[bool] = None
    score: Optional[float] = None

class QuizSubmitRequest(BaseModel):
    quiz_id: UUID4
    responses: List[QuizAnswerSubmission]


class AnswerResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    quiz_id: UUID4
    question_id: UUID4
    answer_text: str
    is_correct: Optional[bool]
    score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
