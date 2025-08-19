from backend.src.core.database import db

class Tweet(db.Model):
    __tablename__ = 'tweets'
    media = db.relationship('Media', backref='tweet', lazy=True)

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Связи
    likes = db.relationship('Like', backref='tweet', lazy=True, cascade='all, delete-orphan')
    media = db.relationship('Media', backref='tweet', lazy=True)