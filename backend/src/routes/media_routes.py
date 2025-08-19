from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from src.config import Config
from src.models.media_model import Media
from src import db

media_blueprint = Blueprint('media', __name__)


@media_blueprint.route('/api/media', methods=['POST'])
def upload_media():
    # Проверка api-key (уже есть в middleware)
    api_key = request.headers.get('api-key')

    # Проверка файла
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Проверка расширения файла
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.split('.')[
        -1].lower() not in allowed_extensions:
        return jsonify({"error": "Invalid file format"}), 400

    # Сохранение файла
    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({"error": f"File save failed: {str(e)}"}), 500

    # Сохранение в БД
    try:
        new_media = Media(
            filename=filename,
            filepath=filepath,
            user_id=1  # Замените на реальный user_id из api-key
        )
        db.session.add(new_media)
        db.session.commit()

        return jsonify({
            "result": True,
            "media_id": new_media.id  # Возвращаем реальный ID из БД
        }), 201

    except Exception as e:
        db.session.rollback()
        # Удаляем файл, если запись в БД не удалась
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": f"Database error: {str(e)}"}), 500