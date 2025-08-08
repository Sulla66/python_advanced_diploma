from sqlalchemy import Column, Integer, String, DateTime, func, JSON, \
    ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(280))
    author_id = Column(Integer, ForeignKey("users.id"))
    media_ids = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    likes_count = Column(Integer, default=0)

    author = relationship("User", back_populates="tweets")
    likes = relationship("Like", back_populates="tweet")