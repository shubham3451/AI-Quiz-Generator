from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from app.api.feedback.services import FeedbackService
from app.core.depedencies import get_feedback_service, get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.get("/")
def generate_feedback(
    quiz_id: Optional[UUID] = Query(None),
    topic: Optional[str] = Query(None),
    service: FeedbackService = Depends(get_feedback_service),
    current_user: User = Depends(get_current_user),

):
    return service.generate_feedback(user_id=current_user.id, quiz_id=quiz_id, topic=topic)
