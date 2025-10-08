from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.repositories.user import UserRepository
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.db.models.user import User
from app.db.repositories.profile import ProfileRepository
from app.db.repositories.quiz import QuizRepository
from app.LLMs.client import LLMClient
from app.vectorDB.vector_store import VectorStore
from app.vectorDB.embeddings import EmbeddingGenerator
from app.api.quiz.services import QuizService
from app.db.repositories.feedback import FeedbackRepository
from app.api.feedback.services import FeedbackService


oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user




def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)



def get_profile_repository(db: Session = Depends(get_db)) -> ProfileRepository:
    return ProfileRepository(db)


def get_quiz_repository(db: Session = Depends(get_db)) -> QuizRepository:
    return QuizRepository(db)



def get_llm_client() -> LLMClient:
    return LLMClient()

def get_embedding_generator() -> EmbeddingGenerator:
    return EmbeddingGenerator()

def get_vector_store() -> VectorStore:
    return VectorStore()

def get_quiz_service(
    profile_repo = Depends(get_profile_repository),
    quiz_repo = Depends(get_quiz_repository),
    llm_client: LLMClient = Depends(get_llm_client),
    vector_store: VectorStore = Depends(get_vector_store),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator)
) -> QuizService:
    return QuizService(
        profile_repo,
        quiz_repo,
        llm_client,
        vector_store,
        embedding_generator
    )


def get_feedback_service(db=Depends(get_db)):
    feedback_repo = FeedbackRepository(db)
    quiz_repo = QuizRepository(db)
    profile_repo = ProfileRepository(db)
    vector_store = VectorStore()
    embedding_gen = EmbeddingGenerator()
    llm_client = LLMClient()
    return FeedbackService(feedback_repo, quiz_repo,profile_repo, vector_store, embedding_gen, llm_client)
