
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    education = Column(String)
    city = Column(String)
    hobbies = Column(ARRAY(String))
    bio = Column(String)

    user = relationship("User", back_populates="profile")
