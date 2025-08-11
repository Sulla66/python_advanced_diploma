import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        'postgresql://postgres:postgres@db:5432/microblog')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки для загрузки файлов
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static',
                                 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB лимит загрузки
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Создание папки для загрузок с обработкой ошибок
    try:
        os.makedirs(UPLOAD_FOLDER, mode=0o755, exist_ok=True)
    except OSError as e:
        if e.errno != 17:  # Игнорируем ошибку "Файл уже существует"
            raise

    # Настройки сессии
    SECRET_KEY = os.getenv('SECRET_KEY',
                           'dev-secret-key')  # Для прода измените на надежный ключ
