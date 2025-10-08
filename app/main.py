from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.api.auth.routes import router as authrouter
from app.api.quiz.routes import router as quizrouter
from app.api.feedback.routes import router as feedbackrouter
from app.core.config import settings  
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    description="Personalized Quiz Generator using RAG-based AI",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

app.include_router(authrouter)
app.include_router(quizrouter)
app.include_router(feedbackrouter)
