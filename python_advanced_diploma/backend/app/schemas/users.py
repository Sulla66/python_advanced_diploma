from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class UserActionType(str, Enum):
    follow = "follow"
    unfollow = "unfollow"

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="Иван Иванов")
    api_key: Optional[str] = Field(
        None,
        min_length=32,
        max_length=32,
        example="d1a8f5c3e7b2d9f4a6c8b3e5d7f2a1c",
        description="Уникальный ключ пользователя (только для создания)"
    )

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Иван Иванов")
    created_at: datetime = Field(..., example="2023-01-01T00:00:00")

class UserProfileResponse(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Иван Иванов")
    followers: List[dict] = Field(
        default_factory=list,
        example=[{"id": 2, "name": "Мария Петрова"}],
        description="Список подписчиков"
    )
    following: List[dict] = Field(
        default_factory=list,
        example=[{"id": 3, "name": "Алексей Сидоров"}],
        description="Список подписок"
    )

class UserAction(BaseModel):
    action: UserActionType = Field(..., example="follow")
    user_id: int = Field(..., example=2, description="ID целевого пользователя")

class UsersListResponse(BaseModel):
    result: bool = Field(default=True, example=True)
    users: List[UserResponse] = Field(..., description="Список пользователей")

class UserErrorResponse(BaseModel):
    result: bool = Field(default=False, example=False)
    error_type: str = Field(..., example="NOT_FOUND")
    error_message: str = Field(..., example="Пользователь не найден")

class FollowResponse(BaseModel):
    result: bool = Field(default=True, example=True)

class FollowErrorResponse(BaseModel):
    result: bool = Field(default=False, example=False)
    error_type: str = Field(..., example="ALREADY_FOLLOWING")
    error_message: str = Field(..., example="Вы уже подписаны на этого пользователя")

# Дополнительные валидаторы
@validator('name')
def validate_name(cls, v):
    if not v.strip():
        raise ValueError("Имя пользователя не может быть пустым")
    return v.strip()

# Обновление ссылок для корректной работы документации
UserProfileResponse.update_forward_refs()
UsersListResponse.update_forward_refs()
UserErrorResponse.update_forward_refs()
FollowResponse.update_forward_refs()
FollowErrorResponse.update_forward_refs()