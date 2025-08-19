from backend.src.core.database import db

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Уникальный constraint: один пользователь — один лайк на твит
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tweet_id', name='unique_like'),
    )