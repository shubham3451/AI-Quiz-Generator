from sqlalchemy.orm import Session
from app.db.models.quiz import Quiz, Question, Answer
from uuid import UUID
from typing import List

class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_quiz(self, quiz_data: dict) -> Quiz:
        quiz = Quiz(**quiz_data)
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz
    

    def get_last_quiz_for_user(self, user_id: UUID):
        """Fetch the most recent quiz for a user"""
        return (
            self.db.query(Quiz)
            .filter(Quiz.user_id == user_id)
            .order_by(Quiz.created_at.desc())
            .first()
        )
    
    def get_quiz_by_id(self, quiz_id: UUID):
        """Fetch quiz by quiz_id"""
        return self.db.query(Quiz).filter(Quiz.id == quiz_id).first()

    def get_answers_for_quiz(self, quiz_id: UUID):
        """Fetch all answers related to a quiz"""
        return (
            self.db.query(Answer)
            .filter(Answer.quiz_id == quiz_id)
            .order_by(Answer.created_at.asc())
            .all()
        )
    
    def add_questions(self, quiz_id: UUID, questions: List[dict]) -> List[Question]:
        question_objs = [Question(quiz_id=quiz_id, **q) for q in questions]
        self.db.add_all(question_objs)
        self.db.commit()
        return question_objs

    def get_questions_by_quiz(self, quiz_id: UUID) -> List[Question]:
        return self.db.query(Question).filter(Question.quiz_id == quiz_id).all()
    
    def get_questions_by_ids(self, question_ids: List[UUID]) -> List[Question]:
        return self.db.query(Question).filter(Question.id.in_(question_ids)).all()


    def save_answers(self, user_id: UUID, quiz_id: UUID, responses: List[dict]) -> List[Answer]:
        answers = [
            Answer(user_id=user_id, quiz_id=quiz_id, **resp)
            for resp in responses
        ]
        self.db.add_all(answers)
        self.db.commit()
        return answers

    def get_answers_by_quiz(self, user_id: UUID, quiz_id: UUID) -> List[Answer]:
        return self.db.query(Answer).filter_by(user_id=user_id, quiz_id=quiz_id).all()
    
    
