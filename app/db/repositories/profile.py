from sqlalchemy.orm import Session
from app.db.models.profile import Profile
from uuid import UUID

class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: UUID) -> Profile | None:
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def create_or_update(self, profile_data: dict) -> Profile:
        profile = self.get_by_user_id(profile_data["user_id"])
        if profile:
            for key, value in profile_data.items():
                setattr(profile, key, value)
        else:
            profile = Profile(**profile_data)
            self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
