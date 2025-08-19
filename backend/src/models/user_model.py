from backend.src.core.database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(100), unique=True, nullable=False)

    # Связи
    tweets = db.relationship('Tweet', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy=True)
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy=True)