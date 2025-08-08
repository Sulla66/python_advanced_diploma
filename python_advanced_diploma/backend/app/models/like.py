from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tweet_id = Column(Integer, ForeignKey("tweets.id"))

    user = relationship("User", back_populates="likes")
    tweet = relationship("Tweet", back_populates="likes")