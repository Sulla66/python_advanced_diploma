from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class TweetActionType(str, Enum):
    create = "create"
    delete = "delete"
    like = "like"
    unlike = "unlike"

class TweetBase(BaseModel):
    content: str = Field(..., max_length=280, example="Пример текста твита")
    tweet_media_ids: Optional[List[int]] = Field(
        default=None,
        example=[1, 2, 3],
        description="Список ID прикрепленных медиафайлов"
    )

    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Текст твита не может быть пустым")
        return v

class TweetCreate(TweetBase):
    pass

class TweetResponse(BaseModel):
    result: bool = Field(default=True, example=True)
    tweet_id: int = Field(..., example=123)

class TweetInFeed(BaseModel):
    id: int = Field(..., example=1)
    content: str = Field(..., example="Пример текста твита")
    attachments: List[str] = Field(
        default_factory=list,
        example=["/media/1.jpg", "/media/2.jpg"],
        description="Ссылки на прикрепленные медиафайлы"
    )
    author: dict = Field(
        ...,
        example={"id": 1, "name": "Иван Иванов"},
        description="Информация об авторе твита"
    )
    likes: List[dict] = Field(
        default_factory=list,
        example=[{"user_id": 2, "name": "Мария Петрова"}],
        description="Список пользователей, поставивших лайк"
    )
    created_at: datetime = Field(..., example="2023-01-01T00:00:00")

class TweetAction(BaseModel):
    action: TweetActionType = Field(..., example="like")
    tweet_id: int = Field(..., example=1)

class TweetsResponse(BaseModel):
    result: bool = Field(default=True, example=True)
    tweets: List[TweetInFeed] = Field(..., description="Список твитов")

class TweetErrorResponse(BaseModel):
    result: bool = Field(default=False, example=False)
    error_type: str = Field(..., example="NOT_FOUND")
    error_message: str = Field(..., example="Твит не найден")

class LikeResponse(BaseModel):
    result: bool = Field(default=True, example=True)

class LikeErrorResponse(BaseModel):
    result: bool = Field(default=False, example=False)
    error_type: str = Field(..., example="ALREADY_LIKED")
    error_message: str = Field(..., example="Вы уже лайкнули этот твит")

# Примеры для документации
TweetResponse.update_forward_refs()
TweetsResponse.update_forward_refs()
TweetErrorResponse.update_forward_refs()
LikeResponse.update_forward_refs()
LikeErrorResponse.update_forward_refs()