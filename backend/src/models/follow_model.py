from backend.src.core.database import db

class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Кто подписался
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # На кого подписался
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Уникальный constraint: одна подписка на пару пользователей
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
    )