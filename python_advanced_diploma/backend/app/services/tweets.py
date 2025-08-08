from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.tweet import Tweet, Like
from app.models.user import User
from app.schemas.tweets import TweetCreate, TweetInFeed


class TweetService:
    def __init__(self, db: Session):
        self.db = db

    def create_tweet(self, tweet_data: TweetCreate, user_id: int) -> dict:
        """
        Создание нового твита
        """
        try:
            new_tweet = Tweet(
                content=tweet_data.content,
                author_id=user_id,
                media_ids=tweet_data.tweet_media_ids or [],
                created_at=datetime.utcnow()
            )

            self.db.add(new_tweet)
            self.db.commit()
            self.db.refresh(new_tweet)

            return {"result": True, "tweet_id": new_tweet.id}

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "result": False,
                    "error_type": "TWEET_CREATION_FAILED",
                    "error_message": str(e)
                }
            )

    def delete_tweet(self, tweet_id: int, user_id: int) -> dict:
        """
        Удаление твита с проверкой прав
        """
        tweet = self.db.query(Tweet).filter(Tweet.id == tweet_id).first()

        if not tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "result": False,
                    "error_type": "TWEET_NOT_FOUND",
                    "error_message": "Tweet not found"
                }
            )

        if tweet.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "result": False,
                    "error_type": "PERMISSION_DENIED",
                    "error_message": "You can't delete this tweet"
                }
            )

        self.db.delete(tweet)
        self.db.commit()

        return {"result": True}

    def like_tweet(self, tweet_id: int, user_id: int) -> dict:
        """
        Добавление лайка к твиту
        """
        tweet = self.db.query(Tweet).filter(Tweet.id == tweet_id).first()

        if not tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "result": False,
                    "error_type": "TWEET_NOT_FOUND",
                    "error_message": "Tweet not found"
                }
            )

        # Проверяем, не лайкал ли уже пользователь этот твит
        existing_like = self.db.query(Like).filter(
            Like.tweet_id == tweet_id,
            Like.user_id == user_id
        ).first()

        if existing_like:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "result": False,
                    "error_type": "ALREADY_LIKED",
                    "error_message": "You already liked this tweet"
                }
            )

        new_like = Like(
            tweet_id=tweet_id,
            user_id=user_id,
            created_at=datetime.utcnow()
        )

        tweet.likes_count += 1
        self.db.add(new_like)
        self.db.commit()

        return {"result": True}

    def unlike_tweet(self, tweet_id: int, user_id: int) -> dict:
        """
        Удаление лайка с твита
        """
        like = self.db.query(Like).filter(
            Like.tweet_id == tweet_id,
            Like.user_id == user_id
        ).first()

        if not like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "result": False,
                    "error_type": "LIKE_NOT_FOUND",
                    "error_message": "Like not found"
                }
            )

        tweet = self.db.query(Tweet).filter(Tweet.id == tweet_id).first()
        if tweet and tweet.likes_count > 0:
            tweet.likes_count -= 1

        self.db.delete(like)
        self.db.commit()

        return {"result": True}

    def get_user_feed(self, user_id: int) -> List[TweetInFeed]:
        """
        Получение ленты твитов для пользователя
        """
        # Получаем ID пользователей, на которых подписан текущий пользователь
        following_ids = [
            f.following_id
            for f in
            self.db.query(Follow).filter(Follow.follower_id == user_id).all()
        ]

        if not following_ids:
            return []

        # Получаем твиты от этих пользователей
        tweets = self.db.query(Tweet).filter(
            Tweet.author_id.in_(following_ids)
        ).order_by(
            Tweet.likes_count.desc(),
            Tweet.created_at.desc()
        ).all()

        # Форматируем результат
        feed = []
        for tweet in tweets:
            author = self.db.query(User).filter(
                User.id == tweet.author_id).first()
            likes = self.db.query(Like).filter(Like.tweet_id == tweet.id).all()

            feed.append(TweetInFeed(
                id=tweet.id,
                content=tweet.content,
                attachments=[f"/media/{mid}" for mid in tweet.media_ids],
                author={"id": author.id, "name": author.name},
                likes=[{"user_id": like.user_id, "name": like.user.name} for
                       like in likes],
                created_at=tweet.created_at
            ))

        return feed