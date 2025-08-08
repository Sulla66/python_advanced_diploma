from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, Follow
from app.schemas.users import UserProfileResponse

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def follow_user(self, follower_id: int, following_id: int) -> dict:
        """
        Подписка на пользователя
        """
        if follower_id == following_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "result": False,
                    "error_type": "INVALID_REQUEST",
                    "error_message": "Cannot follow yourself"
                }
            )

        # Проверяем существование пользователя для подписки
        target_user = self.db.query(User).filter(User.id == following_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "result": False,
                    "error_type": "USER_NOT_FOUND",
                    "error_message": "User not found"
                }
            )

        # Проверяем, что подписка еще не существует
        existing_follow = self.db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        ).first()

        if existing_follow:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "result": False,
                    "error_type": "ALREADY_FOLLOWING",
                    "error_message": "Already following this user"
                }
            )

        # Создаем новую подписку
        new_follow = Follow(
            follower_id=follower_id,
            following_id=following_id,
            created_at=datetime.utcnow()
        )

        self.db.add(new_follow)
        self.db.commit()

        return {"result": True}

    def unfollow_user(self, follower_id: int, following_id: int) -> dict:
        """
        Отписка от пользователя
        """
        follow = self.db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        ).first()

        if not follow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "result": False,
                    "error_type": "NOT_FOLLOWING",
                    "error_message": "Not following this user"
                }
            )

        self.db.delete(follow)
        self.db.commit()

        return {"result": True}

    def get_user_profile(self, user_id: int) -> UserProfileResponse:
        """
        Получение профиля пользователя
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "result": False,
                    "error_type": "USER_NOT_FOUND",
                    "error_message": "User not found"
                }
            )

        # Получаем подписчиков
        followers = self.db.query(User).join(
            Follow, Follow.follower_id == User.id
        ).filter(
            Follow.following_id == user_id
        ).all()

        # Получаем подписки
        following = self.db.query(User).join(
            Follow, Follow.following_id == User.id
        ).filter(
            Follow.follower_id == user_id
        ).all()

        return UserProfileResponse(
            id=user.id,
            name=user.name,
            followers=[{"id": u.id, "name": u.name} for u in followers],
            following=[{"id": u.id, "name": u.name} for u in following]
        )

    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """
        Получение пользователя по API ключу
        """
        return self.db.query(User).filter(User.api_key == api_key).first()

    def create_user(self, name: str, api_key: str) -> User:
        """
        Создание нового пользователя
        """
        try:
            user = User(name=name, api_key=api_key)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "result": False,
                    "error_type": "USER_CREATION_FAILED",
                    "error_message": str(e)
                }
            )