import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config

from routes.document_routes import document_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    app.register_blueprint(
        document_bp,
        url_prefix="/api/documents"
    )

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.CHROMA_DB_PATH, exist_ok=True)

    # Register Blueprints here
    # app.register_blueprint(document_bp, url_prefix="/api/documents")

    @app.route("/")
    def home():
        return jsonify({
            "message": "Industrial Knowledge Intelligence Platform API",
            "status": "Running"
        })

    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy",
            "debug": Config.DEBUG,
            "gemini_configured": bool(Config.GOOGLE_API_KEY)
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=Config.PORT,
        debug=Config.DEBUG
    )