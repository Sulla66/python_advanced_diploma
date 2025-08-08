import pytest
from fastapi import status
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image
import tempfile
import os


class TestMediaAPI:
    """Тестирование API для работы с медиафайлами"""

    def generate_test_image(self):
        """Генерация тестового изображения в памяти"""
        image = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)
        return img_io

    def test_upload_media_success(self, auth_client):
        """Успешная загрузка медиафайла"""
        test_image = self.generate_test_image()

        response = auth_client.post(
            "/api/media",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "media_id" in response.json()
        assert response.json()["result"] is True

    def test_upload_media_unauthorized(self, client):
        """Попытка загрузить файл без авторизации"""
        test_image = self.generate_test_image()

        response = client.post(
            "/api/media",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_invalid_file_type(self, auth_client):
        """Попытка загрузить файл недопустимого типа"""
        test_file = BytesIO(b"Some binary data")

        response = auth_client.post(
            "/api/media",
            files={"file": ("test.txt", test_file, "text/plain")}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Allowed file types" in response.text

    def test_get_media_success(self, auth_client, test_media):
        """Успешное получение медиафайла"""
        # Сначала создаем временный файл для теста
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(b"test image data")
            test_media.filename = os.path.basename(tmp.name)
            tmp.close()

            response = auth_client.get(f"/api/media/{test_media.filename}")
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/jpeg"

            # Удаляем временный файл
            os.unlink(tmp.name)

    def test_get_nonexistent_media(self, auth_client):
        """Попытка получить несуществующий файл"""
        response = auth_client.get("/api/media/nonexistent.jpg")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_large_file(self, auth_client):
        """Попытка загрузить слишком большой файл"""
        # Создаем файл больше 5MB
        large_file = BytesIO(b"x" * (6 * 1024 * 1024))

        response = auth_client.post(
            "/api/media",
            files={"file": ("large.jpg", large_file, "image/jpeg")}
        )

        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "File size exceeds" in response.text

    def test_media_upload_without_file(self, auth_client):
        """Попытка загрузить без файла"""
        response = auth_client.post("/api/media")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_media_upload_empty_file(self, auth_client):
        """Попытка загрузить пустой файл"""
        empty_file = BytesIO(b"")

        response = auth_client.post(
            "/api/media",
            files={"file": ("empty.jpg", empty_file, "image/jpeg")}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST