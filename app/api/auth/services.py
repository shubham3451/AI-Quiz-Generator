from fastapi import HTTPException, status
from app.api.auth.schemas import RegisterRequest, LoginRequest
from app.db.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.db.repositories.user import UserRepository

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, data: RegisterRequest) -> dict:
        existing_user = self.user_repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user = User(email=data.email, hashed_password=hash_password(data.password))
        try:
            self.user_repo.create(user=user)
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            ) from e

        return {"msg": "Registration successful"}

    def login(self, data: LoginRequest) -> dict:
        user = self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        access_token = create_access_token({"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
