from backend.app.core.database import db

class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())