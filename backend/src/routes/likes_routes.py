from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.like_model import Like
from src.models.tweet_model import Tweet

like_blueprint = Blueprint('likes', __name__)

# 4.1. Поставить лайк
@like_blueprint.route('/api/likes/<int:tweet_id>', methods=['POST'])
@jwt_required()
def like_tweet(tweet_id):
    current_user_id = get_jwt_identity()
    tweet = Tweet.query.get(tweet_id)

    if not tweet:
        return jsonify({"error": "Tweet not found"}), 404

    # Проверяем, не лайкал ли уже
    existing_like = Like.query.filter_by(user_id=current_user_id, tweet_id=tweet_id).first()
    if existing_like:
        return jsonify({"error": "Already liked"}), 400

    new_like = Like(user_id=current_user_id, tweet_id=tweet_id)
    new_like.save()

    return jsonify({"result": True}), 201

# 4.2. Убрать лайк
@like_blueprint.route('/api/likes/<int:tweet_id>', methods=['DELETE'])
@jwt_required()
def unlike_tweet(tweet_id):
    current_user_id = get_jwt_identity()
    like = Like.query.filter_by(user_id=current_user_id, tweet_id=tweet_id).first()

    if not like:
        return jsonify({"error": "Like not found"}), 404

    like.delete()
    return jsonify({"result": True}), 200