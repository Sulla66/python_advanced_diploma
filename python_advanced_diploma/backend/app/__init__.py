from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object('backend.app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # Импорт моделей ДО создания Blueprint
    from .models.user_model import User
    from .models.tweet_model import Tweet
    from .models.like_model import Like
    from .models.follow_model import Follow
    from .models.media_model import Media

    # Регистрация Blueprint
    from backend.app.routes.ping_routes import ping_blueprint
    app.register_blueprint(ping_blueprint)

    return app