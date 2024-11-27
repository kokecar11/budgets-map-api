from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.config import generate_uuid
from src.database import Base


class SessionModel(Base):
    __tablename__ = "sessions"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid())
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_token = Column(String)
    expires = Column(DateTime, nullable=True)

    user = relationship("UserModel", back_populates="sessions")
