import pytest
from fastapi import status
from app.schemas.tweets import TweetResponse, TweetsResponse


class TestTweetsAPI:
    """Тестирование API для работы с твитами"""

    def test_create_tweet_success(self, auth_client, test_user):
        """Успешное создание твита"""
        tweet_data = {
            "tweet_data": "Test tweet content",
            "tweet_media_ids": []
        }
        response = auth_client.post("/api/tweets", json=tweet_data)

        assert response.status_code == status.HTTP_200_OK
        assert TweetResponse(**response.json())

    def test_create_tweet_empty_content(self, auth_client):
        """Попытка создать твит с пустым содержимым"""
        response = auth_client.post("/api/tweets", json={"tweet_data": "",
                                                         "tweet_media_ids": []})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "tweet_data" in response.text

    def test_create_tweet_unauthorized(self, client):
        """Попытка создать твит без авторизации"""
        response = client.post("/api/tweets", json={"tweet_data": "Test",
                                                    "tweet_media_ids": []})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_tweet_success(self, auth_client, test_user, test_tweet):
        """Успешное удаление твита"""
        response = auth_client.delete(f"/api/tweets/{test_tweet.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["result"] is True

    def test_delete_tweet_not_owner(self, auth_client, test_user2, test_tweet):
        """Попытка удалить чужой твит"""
        auth_client.headers.update({"api-key": test_user2.api_key})
        response = auth_client.delete(f"/api/tweets/{test_tweet.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "You can't delete this tweet" in response.text

    def test_delete_nonexistent_tweet(self, auth_client):
        """Попытка удалить несуществующий твит"""
        response = auth_client.delete("/api/tweets/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_like_tweet_success(self, auth_client, test_tweet):
        """Успешная установка лайка"""
        response = auth_client.post(f"/api/tweets/{test_tweet.id}/likes")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["result"] is True

    def test_like_tweet_twice(self, auth_client, test_tweet, test_like):
        """Попытка лайкнуть твит дважды"""
        response = auth_client.post(f"/api/tweets/{test_tweet.id}/likes")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already liked" in response.text

    def test_unlike_tweet_success(self, auth_client, test_tweet, test_like):
        """Успешное снятие лайка"""
        response = auth_client.delete(f"/api/tweets/{test_tweet.id}/likes")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["result"] is True

    def test_unlike_not_liked_tweet(self, auth_client, test_tweet):
        """Попытка снять несуществующий лайк"""
        response = auth_client.delete(f"/api/tweets/{test_tweet.id}/likes")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_feed_success(self, auth_client, test_tweet, test_follow):
        """Получение ленты твитов"""
        response = auth_client.get("/api/tweets")

        assert response.status_code == status.HTTP_200_OK
        assert TweetsResponse(**response.json())
        assert len(response.json()["tweets"]) == 1

    def test_get_feed_empty(self, auth_client, test_user):
        """Получение пустой ленты"""
        response = auth_client.get("/api/tweets")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["tweets"]) == 0

    def test_get_feed_unauthorized(self, client):
        """Попытка получить ленту без авторизации"""
        response = client.get("/api/tweets")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_tweet_with_media(self, auth_client, test_media):
        """Создание твита с прикрепленными медиа"""
        tweet_data = {
            "tweet_data": "Test tweet with media",
            "tweet_media_ids": [test_media.id]
        }
        response = auth_client.post("/api/tweets", json=tweet_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["result"] is True