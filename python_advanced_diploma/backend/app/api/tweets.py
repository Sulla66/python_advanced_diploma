from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.services.auth import verify_api_key
from app.models import Tweet, Like, User, Follow
from app.models.user import User
from app.models.follow import Follow
from app.database import get_db

router = APIRouter(prefix="/api/tweets", tags=["tweets"])


# Pydantic схемы
class TweetCreate(BaseModel):
    tweet_data: str = Field(..., max_length=280)
    tweet_media_ids: Optional[List[int]] = Field(default=None)


class TweetResponse(BaseModel):
    result: bool = True
    tweet_id: int


class AuthorResponse(BaseModel):
    id: int
    name: str


class LikeResponse(BaseModel):
    user_id: int
    name: str


class TweetInFeed(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: AuthorResponse
    likes: List[LikeResponse]


class ErrorResponse(BaseModel):
    result: bool = False
    error_type: str
    error_message: str


@router.post(
    "/",
    response_model=TweetResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid tweet data"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    }
)
async def create_tweet(
        tweet: TweetCreate,
        api_key: str = Depends(verify_api_key),
        db: AsyncSession = Depends(get_db)
):
    """Создание нового твита"""
    try:
        new_tweet = Tweet(
            content=tweet.tweet_data,
            author_id=api_key,
            media_ids=tweet.tweet_media_ids or [],
            created_at=datetime.utcnow()
        )
        db.add(new_tweet)
        await db.commit()
        await db.refresh(new_tweet)

        return {"result": True, "tweet_id": new_tweet.id}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "result": False,
                "error_type": "DB_ERROR",
                "error_message": str(e)
            }
        )


@router.delete(
    "/{tweet_id}",
    response_model=dict,
    responses={
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Tweet not found"},
    }
)
async def delete_tweet(
        tweet_id: int,
        api_key: str = Depends(verify_api_key),
        db: AsyncSession = Depends(get_db)
):
    """Удаление твита"""
    result = await db.execute(
        select(Tweet).where(Tweet.id == tweet_id)
    )
    tweet = result.scalars().first()

    if not tweet:
        raise HTTPException(
            status_code=404,
            detail={
                "result": False,
                "error_type": "NOT_FOUND",
                "error_message": "Tweet not found"
            }
        )

    if tweet.author_id != api_key:
        raise HTTPException(
            status_code=403,
            detail={
                "result": False,
                "error_type": "FORBIDDEN",
                "error_message": "You can't delete this tweet"
            }
        )

    await db.delete(tweet)
    await db.commit()

    return {"result": True}


@router.post(
    "/{tweet_id}/likes",
    response_model=dict,
    responses={
        404: {"model": ErrorResponse, "description": "Tweet not found"},
        409: {"model": ErrorResponse, "description": "Already liked"},
    }
)
async def like_tweet(
        tweet_id: int,
        api_key: str = Depends(verify_api_key),
        db: AsyncSession = Depends(get_db)
):
    """Поставить лайк твиту"""
    # Проверяем существование твита
    tweet_result = await db.execute(
        select(Tweet).where(Tweet.id == tweet_id)
    )
    tweet = tweet_result.scalars().first()

    if not tweet:
        raise HTTPException(
            status_code=404,
            detail={
                "result": False,
                "error_type": "NOT_FOUND",
                "error_message": "Tweet not found"
            }
        )

    # Проверяем, не лайкал ли уже пользователь
    existing_like_result = await db.execute(
        select(Like).where(
            Like.tweet_id == tweet_id,
            Like.user_id == api_key
        )
    )
    existing_like = existing_like_result.scalars().first()

    if existing_like:
        raise HTTPException(
            status_code=409,
            detail={
                "result": False,
                "error_type": "CONFLICT",
                "error_message": "You already liked this tweet"
            }
        )

    # Создаем новый лайк
    new_like = Like(tweet_id=tweet_id, user_id=api_key)
    db.add(new_like)
    tweet.likes_count += 1
    await db.commit()

    return {"result": True}


@router.delete(
    "/{tweet_id}/likes",
    response_model=dict,
    responses={
        404: {"model": ErrorResponse, "description": "Not liked"},
    }
)
async def unlike_tweet(
        tweet_id: int,
        api_key: str = Depends(verify_api_key),
        db: AsyncSession = Depends(get_db)
):
    """Убрать лайк с твита"""
    # Находим лайк
    like_result = await db.execute(
        select(Like).where(
            Like.tweet_id == tweet_id,
            Like.user_id == api_key
        )
    )
    like = like_result.scalars().first()

    if not like:
        raise HTTPException(
            status_code=404,
            detail={
                "result": False,
                "error_type": "NOT_FOUND",
                "error_message": "Like not found"
            }
        )

    # Удаляем лайк
    await db.delete(like)

    # Обновляем счетчик лайков
    tweet_result = await db.execute(
        select(Tweet).where(Tweet.id == tweet_id)
    )
    tweet = tweet_result.scalars().first()

    if tweet and tweet.likes_count > 0:
        tweet.likes_count -= 1

    await db.commit()

    return {"result": True}


@router.get(
    "/",
    response_model=dict,
    response_model_exclude_none=True,
    responses={
        200: {
            "model": dict,
            "examples": {
                "normal": {
                    "value": {
                        "result": True,
                        "tweets": [
                            {
                                "id": 1,
                                "content": "Пример твита",
                                "attachments": ["/media/1.jpg"],
                                "author": {"id": 1, "name": "Иван"},
                                "likes": [{"user_id": 2, "name": "Мария"}]
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_feed(
        api_key: str = Depends(verify_api_key),
        db: AsyncSession = Depends(get_db)
):
    """Получить ленту твитов"""
    # Получаем список подписок пользователя
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == api_key)
    )
    following = following_result.scalars().all()

    if not following:
        return {"result": True, "tweets": []}

    # Получаем твиты с информацией об авторах и лайках
    tweets_result = await db.execute(
        select(Tweet)
        .where(Tweet.author_id.in_(following))
        .options(
            selectinload(Tweet.author),
            selectinload(Tweet.likes).selectinload(Like.user)
        )
        .order_by(
            Tweet.likes_count.desc(),
            Tweet.created_at.desc()
        )
    )
    tweets = tweets_result.scalars().all()

    formatted_tweets = []
    for tweet in tweets:
        formatted_tweets.append({
            "id": tweet.id,
            "content": tweet.content,
            "attachments": [
                f"/media/{media_id}"
                for media_id in (tweet.media_ids or [])
            ],
            "author": {
                "id": tweet.author.id,
                "name": tweet.author.name
            },
            "likes": [
                {
                    "user_id": like.user.id,
                    "name": like.user.name
                }
                for like in tweet.likes
            ]
        })

    return {"result": True, "tweets": formatted_tweets}