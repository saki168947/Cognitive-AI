from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .db import db
from .api import api_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    CORS(app)
    db.init_app(app)
    app.register_blueprint(api_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    with app.app_context():
        db.create_all()

    return app
