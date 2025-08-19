from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.tweet_model import Tweet
from src.models.follow_model import Follow

feed_blueprint = Blueprint('feed', __name__)

# 5.1. Получить ленту
@feed_blueprint.route('/api/feed', methods=['GET'])
@jwt_required()
def get_feed():
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Получаем ID пользователей, на которых подписан текущий пользователь
    following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=current_user_id).all()]

    # Получаем твиты (сортировка по дате и популярности)
    tweets = Tweet.query.filter(Tweet.user_id.in_(following_ids)) \
        .order_by(Tweet.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    # Форматируем ответ
    result = {
        "result": True,
        "tweets": [{
            "id": tweet.id,
            "content": tweet.content,
            "author": {"id": tweet.user.id, "name": tweet.user.username},
            "likes": len(tweet.likes),
            "attachments": [media.id for media in tweet.media],
            "created_at": tweet.created_at.isoformat()
        } for tweet in tweets.items]
    }

    return jsonify(result), 200