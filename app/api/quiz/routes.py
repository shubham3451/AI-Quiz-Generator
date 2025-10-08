from fastapi import APIRouter, Depends, status
from app.core.depedencies import get_current_user
from app.api.quiz.schemas import ProfileCreate
from app.api.quiz.schemas import QuizGenerateResponse, QuizSubmitRequest
from app.api.quiz.services import QuizService
from app.db.models.user import User
from app.core.depedencies import get_quiz_service

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.post(
    "/generate",
    response_model=QuizGenerateResponse,
    summary="Generate a quiz from user profile",
    status_code=status.HTTP_201_CREATED,
)
def generate_quiz(
    profile: ProfileCreate,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    return quiz_service.generate_quiz_for_user(user_id=current_user.id, profile_data=profile.dict())


@router.post(
    "/submit-responses",
    summary="Submit quiz answers",
    status_code=status.HTTP_200_OK,
)
def submit_quiz_answers(
    submission: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    return quiz_service.process_quiz_response(
        user_id=current_user.id,
        quiz_id=submission.quiz_id,
        responses=[resp.dict() for resp in submission.responses]
    )
