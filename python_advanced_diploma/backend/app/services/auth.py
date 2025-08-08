from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.database import get_db
import hashlib

api_key_scheme = APIKeyHeader(name="api-key", auto_error=False)


def get_current_user(
        api_key: Optional[str] = Depends(api_key_scheme),
        db: Session = Depends(get_db)
) -> User:
    """
    Получение текущего пользователя по API-ключу
    Вызывает HTTPException 401 если ключ невалидный
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "result": False,
                "error_type": "UNAUTHORIZED",
                "error_message": "API key is missing"
            }
        )

    # В реальной системе нужно хэшировать ключ перед поиском
    user = db.query(User).filter(User.api_key == api_key).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "result": False,
                "error_type": "UNAUTHORIZED",
                "error_message": "Invalid API key"
            }
        )

    return user


def verify_api_key(
        api_key: Optional[str] = Depends(api_key_scheme),
        db: Session = Depends(get_db)
) -> str:
    """
    Верификация API ключа
    Возвращает user_id если ключ валидный
    """
    user = get_current_user(api_key, db)
    return str(user.id)


def generate_api_key(user_id: int) -> str:
    """
    Генерация нового API ключа для пользователя
    В реальной системе нужно использовать более безопасный метод
    """
    secret_salt = "your-secret-salt-value"
    raw_key = f"{user_id}-{secret_salt}"
    return hashlib.sha256(raw_key.encode()).hexdigest()


def is_valid_api_key_format(api_key: str) -> bool:
    """
    Проверка формата API ключа
    """
    return len(api_key) == 64 and all(c in "0123456789abcdef" for c in api_key)