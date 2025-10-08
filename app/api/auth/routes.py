from fastapi import APIRouter, Depends, status
from app.api.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.api.auth.services import AuthService
from app.core.depedencies import get_user_repository
from app.db.repositories.user import UserRepository

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    service = AuthService(user_repo)
    return service.register(payload)

@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    service = AuthService(user_repo)
    return service.login(payload)