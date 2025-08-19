from flask import Blueprint, request, jsonify
from src.models.tweet_model import Tweet

tweet_blueprint = Blueprint('tweets', __name__)

@tweet_blueprint.route('/api/tweets', methods=['POST'])
def create_tweet():  # Изменено: убрана JWT-аутентификация
    data = request.get_json()
    if not data or "tweet_data" not in data:
        return jsonify({"error": "Invalid data"}), 400

    new_tweet = Tweet(
        user_id=1,  # Замените на логику определения user_id по api-key
        content=data["tweet_data"],
        media_ids=data.get("tweet_media_ids", [])
    )
    new_tweet.save()

    return jsonify({"result": True, "tweet_id": new_tweet.id}), 201