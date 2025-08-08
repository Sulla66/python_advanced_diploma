from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel  # Добавлен этот импорт
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.services.auth import verify_api_key
from app.models import User, Follow
from app.database import get_db

router = APIRouter(prefix="/api/users", tags=["users"])

class UserResponse(BaseModel):
    id: int
    name: str

class UserProfileResponse(BaseModel):
    result: bool = True
    user: dict

class ErrorResponse(BaseModel):
    result: bool = False
    error_type: str
    error_message: str

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Получить информацию о текущем пользователе"""
    user_result = await db.execute(
        select(User)
        .where(User.id == api_key)
        .options(
            selectinload(User.followers),
            selectinload(User.following)
        )
    )
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "result": False,
                "error_type": "NOT_FOUND",
                "error_message": "User not found"
            }
        )

    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [
                {"id": follower.follower.id, "name": follower.follower.name}
                for follower in user.followers
            ],
            "following": [
                {"id": follow.following.id, "name": follow.following.name}
                for follow in user.following
            ]
        }
    }


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Получить информацию о пользователе по ID"""
    user_result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.followers),
            selectinload(User.following)
        )
    )
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "result": False,
                "error_type": "NOT_FOUND",
                "error_message": "User not found"
            }
        )

    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [
                {"id": follower.follower.id, "name": follower.follower.name}
                for follower in user.followers
            ],
            "following": [
                {"id": follow.following.id, "name": follow.following.name}
                for follow in user.following
            ]
        }
    }

@router.post("/{user_id}/follow", response_model=dict)
async def follow_user(
    user_id: int,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Подписаться на пользователя"""
    if api_key == user_id:
        raise HTTPException(
            status_code=400,
            detail={
                "result": False,
                "error_type": "VALIDATION_ERROR",
                "error_message": "Cannot follow yourself"
            }
        )

    # Проверяем существование пользователя
    user_result = await db.execute(select(User).where(User.id == user_id))
    if not user_result.scalars().first():
        raise HTTPException(
            status_code=404,
            detail={
                "result": False,
                "error_type": "NOT_FOUND",
                "error_message": "User not found"
            }
        )

    # Проверяем, не подписаны ли уже
    existing_follow_result = await db.execute(
        select(Follow)
        .where(Follow.follower_id == api_key)
        .where(Follow.following_id == user_id)
    )
    if existing_follow_result.scalars().first():
        raise HTTPException(
            status_code=409,
            detail={
                "result": False,
                "error_type": "CONFLICT",
                "error_message": "Already following this user"
            }
        )

    # Создаем подписку
    new_follow = Follow(follower_id=api_key, following_id=user_id)
    db.add(new_follow)
    await db.commit()

    return {"result": True}

@router.delete("/{user_id}/follow", response_model=dict)
async def unfollow_user(
    user_id: int,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Отписаться от пользователя"""
    # Находим подписку
    follow_result = await db.execute(
        select(Follow)
        .where(Follow.follower_id == api_key)
        .where(Follow.following_id == user_id)
    )
    follow = follow_result.scalars().first()

    if not follow:
        raise HTTPException(
            status_code=404,
            detail={
                "result": False,
                "error_type": "NOT_FOUND",
                "error_message": "Follow not found"
            }
        )

    # Удаляем подписку
    await db.delete(follow)
    await db.commit()

    return {"result": True}