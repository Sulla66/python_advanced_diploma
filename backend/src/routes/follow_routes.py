from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user_model import User
from src.models.follow_model import Follow

follow_blueprint = Blueprint('follow', __name__)


# 3.1. Подписаться на пользователя
@follow_blueprint.route('/api/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user_id = get_jwt_identity()

    if current_user_id == user_id:
        return jsonify({"error": "You can't follow yourself"}), 400

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"error": "User not found"}), 404

    # Проверяем, не подписаны ли уже
    existing_follow = Follow.query.filter_by(
        follower_id=current_user_id,
        following_id=user_id
    ).first()

    if existing_follow:
        return jsonify({"error": "Already following"}), 400

    # Создаем подписку
    new_follow = Follow(follower_id=current_user_id, following_id=user_id)
    new_follow.save()

    return jsonify({"result": True}), 201


# 3.2. Отписаться от пользователя
@follow_blueprint.route('/api/follow/<int:user_id>', methods=['DELETE'])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = get_jwt_identity()
    follow = Follow.query.filter_by(follower_id=current_user_id,
                                    following_id=user_id).first()

    if not follow:
        return jsonify({"error": "Not following this user"}), 400

    follow.delete()
    return jsonify({"result": True}), 200