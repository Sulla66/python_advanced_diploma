from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    tweets = relationship("Tweet", back_populates="author")
    likes = relationship("Like", back_populates="user")
    followers = relationship("Follow", foreign_keys="Follow.following_id",
                             back_populates="following_user")
    following = relationship("Follow", foreign_keys="Follow.follower_id",
                             back_populates="follower")