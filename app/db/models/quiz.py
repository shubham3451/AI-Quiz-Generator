import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, TIMESTAMP, Text, ARRAY, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    profile_snapshot = Column(JSON)
    total_questions = Column(Integer)
    quiz_type = Column(String)
    tags = Column(ARRAY(String))
    quiz_metadata = Column(JSON)



class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"))

    question_text = Column(Text, nullable=False)
    question_type = Column(String)  # mcq, open_ended, etc.
    options = Column(ARRAY(String), nullable=True)  # only for MCQs
    correct_answer = Column(Text, nullable=True)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"))
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"))

    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=None)
    score = Column(Float, default=None)
    created_at = Column(TIMESTAMP, server_default=func.now())