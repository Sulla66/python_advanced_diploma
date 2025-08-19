import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    @staticmethod
    def check_db_connection(db_uri):
        """Проверяет валидность URL БД."""
        if not db_uri.startswith(('postgresql://', 'sqlite://')):
            raise ValueError(f"Invalid database URL: {db_uri}")

    # Настройки БД
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/microblog')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    check_db_connection(SQLALCHEMY_DATABASE_URI)

    # Загрузка файлов
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Создание папки для загрузок
    try:
        os.makedirs(UPLOAD_FOLDER, mode=0o755, exist_ok=True)
    except OSError as e:
        if e.errno != 17:
            print(f"Ошибка при создании папки {UPLOAD_FOLDER}: {e}")
            raise

    # Безопасность
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-strong-dev-key-here')  # Замените на случайный ключ

    # Swagger
    SWAGGER = {
        'title': 'Microblog API',
        'version': '1.0',
        'description': 'Документация для сервиса микроблогов'
    }
    # Настройки для загрузки файлов
    UPLOAD_FOLDER = os.path.join(Path(__file__).parent.parent, 'static',
                                 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Создаем папку при запуске
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False