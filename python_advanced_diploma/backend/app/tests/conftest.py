import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models import Tweet, Like
from app.models.media import Media
from app.models.follow import Follow

# Настройка тестовой базы данных SQLite в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False,
                                   bind=engine)


# Фикстура для создания тестовой базы данных
@pytest.fixture(scope="function")
def db():
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Фикстура для тестового клиента
@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.rollback()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# Фикстуры для тестовых данных
@pytest.fixture(scope="function")
def test_user(db):
    user = User(
        name="Test User",
        api_key="test_api_key_123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user2(db):
    user = User(
        name="Another User",
        api_key="test_api_key_456"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_tweet(db, test_user):
    tweet = Tweet(
        content="Test tweet content",
        author_id=test_user.id,
        media_ids=[]
    )
    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return tweet


@pytest.fixture(scope="function")
def test_media(db, test_user):
    media = Media(
        user_id=test_user.id,
        original_filename="test.jpg",
        filename="1.jpg",
        content_type="image/jpeg"
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


@pytest.fixture(scope="function")
def test_follow(db, test_user, test_user2):
    follow = Follow(
        follower_id=test_user.id,
        following_id=test_user2.id
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow


@pytest.fixture(scope="function")
def test_like(db, test_user, test_tweet):
    like = Like(
        user_id=test_user.id,
        tweet_id=test_tweet.id
    )
    db.add(like)
    test_tweet.likes_count += 1
    db.commit()
    db.refresh(like)
    return like


# Фикстура для авторизованного клиента
@pytest.fixture(scope="function")
def auth_client(client, test_user):
    client.headers.update({"api-key": test_user.api_key})
    return client
