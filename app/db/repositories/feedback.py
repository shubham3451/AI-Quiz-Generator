from sqlalchemy.orm import Session
from app.db.models.feedback import Feedback
from uuid import UUID
from typing import List

class FeedbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_feedback(self, feedback_data: dict) -> Feedback:
        feedback = Feedback(**feedback_data)
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_by_quiz(self, user_id: UUID, quiz_id: UUID) -> List[Feedback]:
        return self.db.query(Feedback).filter_by(user_id=user_id, quiz_id=quiz_id).all()

    def get_by_question(self, answer_id: UUID) -> Feedback | None:
        return self.db.query(Feedback).filter_by(answer_id=answer_id).first()
    
    
        

    
