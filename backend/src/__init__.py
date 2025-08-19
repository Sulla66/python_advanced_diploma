from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Middleware для проверки api-key (заменяет JWT)
    @app.before_request
    def check_api_key():
        if request.endpoint in ['static', 'ping.ping']:  # Пропускаем статику и /ping
            return
        api_key = request.headers.get('api-key')
        if not api_key or api_key != 'test':  # Ключ 'test' из ТЗ
            return jsonify({"error": "Invalid or missing api-key"}), 401

    # Регистрация Blueprint'ов (без JWT)
    from .routes.ping_routes import ping_blueprint
    from .routes.tweets_routes import tweet_blueprint
    from .routes.media_routes import media_blueprint
    from .routes.follow_routes import follow_blueprint
    from .routes.likes_routes import like_blueprint
    from .routes.feed_routes import feed_blueprint

    app.register_blueprint(ping_blueprint)
    app.register_blueprint(tweet_blueprint, url_prefix='/api')
    app.register_blueprint(media_blueprint, url_prefix='/api')
    app.register_blueprint(follow_blueprint, url_prefix='/api')
    app.register_blueprint(like_blueprint, url_prefix='/api')
    app.register_blueprint(feed_blueprint, url_prefix='/api')

    return app

app = create_app()