import pytest
from fastapi import status
from app.schemas.users import UserProfileResponse


class TestUsersAPI:
    """Тестирование API для работы с пользователями"""

    def test_get_my_profile_success(self, auth_client, test_user):
        """Успешное получение профиля текущего пользователя"""
        response = auth_client.get("/api/users/me")

        assert response.status_code == status.HTTP_200_OK
        profile = UserProfileResponse(**response.json()["user"])
        assert profile.id == test_user.id
        assert profile.name == test_user.name

    def test_get_my_profile_unauthorized(self, client):
        """Попытка получить профиль без авторизации"""
        response = client.get("/api/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_profile_success(self, auth_client, test_user2):
        """Успешное получение профиля другого пользователя"""
        response = auth_client.get(f"/api/users/{test_user2.id}")

        assert response.status_code == status.HTTP_200_OK
        profile = UserProfileResponse(**response.json()["user"])
        assert profile.id == test_user2.id
        assert profile.name == test_user2.name

    def test_get_nonexistent_user_profile(self, auth_client):
        """Попытка получить профиль несуществующего пользователя"""
        response = auth_client.get("/api/users/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_follow_user_success(self, auth_client, test_user, test_user2):
        """Успешная подписка на пользователя"""
        response = auth_client.post(f"/api/users/{test_user2.id}/follow")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["result"] is True

    def test_follow_self(self, auth_client, test_user):
        """Попытка подписаться на самого себя"""
        response = auth_client.post(f"/api/users/{test_user.id}/follow")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot follow yourself" in response.text

    def test_follow_twice(self, auth_client, test_user2, test_follow):
        """Попытка подписаться дважды на одного пользователя"""
        response = auth_client.post(f"/api/users/{test_user2.id}/follow")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "Already following" in response.text

    def test_follow_nonexistent_user(self, auth_client):
        """Попытка подписаться на несуществующего пользователя"""
        response = auth_client.post("/api/users/999/follow")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unfollow_success(self, auth_client, test_user2, test_follow):
        """Успешная отписка от пользователя"""
        response = auth_client.delete(f"/api/users/{test_user2.id}/follow")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["result"] is True

    def test_unfollow_not_following(self, auth_client, test_user2):
        """Попытка отписаться от пользователя, на которого не подписан"""
        response = auth_client.delete(f"/api/users/{test_user2.id}/follow")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Not following" in response.text

    def test_profile_with_followers(self, auth_client, test_user, test_user2,
                                    test_follow):
        """Проверка отображения подписчиков в профиле"""
        response = auth_client.get(f"/api/users/{test_user2.id}")

        assert response.status_code == status.HTTP_200_OK
        profile = response.json()["user"]
        assert len(profile["followers"]) == 1
        assert profile["followers"][0]["id"] == test_user.id

    def test_profile_with_following(self, auth_client, test_user, test_user2,
                                    test_follow):
        """Проверка отображения подписок в профиле"""
        response = auth_client.get(f"/api/users/{test_user.id}")

        assert response.status_code == status.HTTP_200_OK
        profile = response.json()["user"]
        assert len(profile["following"]) == 1
        assert profile["following"][0]["id"] == test_user2.id