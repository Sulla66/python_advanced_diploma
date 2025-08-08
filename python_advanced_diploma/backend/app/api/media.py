from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from typing import List

from app.services.auth import verify_api_key
from app.models import Media, User
from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/api/media", tags=["media"])


class MediaResponse(BaseModel):
    result: bool = True
    media_id: int


class MediaInfoResponse(BaseModel):
    id: int
    filename: str
    url: str
    uploaded_at: str


class ErrorResponse(BaseModel):
    result: bool = False
    error_type: str
    error_message: str


# Конфигурация
MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post(
    "/",
    response_model=MediaResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file format"},
        413: {"model": ErrorResponse, "description": "File too large"},
    }
)
async def upload_media(
        file: UploadFile = File(...),
        api_key: str = Depends(verify_api_key),
        db: AsyncSession = Depends(get_db)
):
    """Загрузить медиафайл"""
    try:
        # Проверка пользователя
        user = await db.get(User, api_key)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверка размера файла
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail={
                    "result": False,
                    "error_type": "FILE_TOO_LARGE",
                    "error_message": f"File size exceeds {MAX_FILE_SIZE} bytes"
                }
            )

        # Проверка расширения файла
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail={
                    "result": False,
                    "error_type": "INVALID_FILE_FORMAT",
                    "error_message": f"Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
                }
            )

        # Генерация уникального имени файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{user.id}_{timestamp}{file_ext}"
        file_path = MEDIA_DIR / new_filename

        # Сохранение файла
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Создание записи в БД
        new_media = Media(
            filename=new_filename,
            file_path=str(file_path),
            mime_type=file.content_type,
            user_id=user.id
        )
        db.add(new_media)
        await db.commit()
        await db.refresh(new_media)

        return {"result": True, "media_id": new_media.id}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "result": False,
                "error_type": "SERVER_ERROR",
                "error_message": str(e)
            }
        )


@router.get("/{media_id}", response_model=MediaInfoResponse)
async def get_media_info(
        media_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Получить информацию о медиафайле"""
    media = await db.get(Media, media_id)
    if not media:
        raise HTTPException(
            status_code=404,
            detail={
                "result": False,
                "error_type": "NOT_FOUND",
                "error_message": "Media not found"
            }
        )

    return {
        "id": media.id,
        "filename": media.filename,
        "url": media.get_url(),
        "uploaded_at": media.created_at.isoformat()
    }

