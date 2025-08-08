from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))

    follower = relationship("User", foreign_keys=[follower_id],
                            back_populates="following")
    following_user = relationship("User", foreign_keys=[following_id],
                                  back_populates="followers")