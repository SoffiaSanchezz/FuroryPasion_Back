from flask import Flask, send_from_directory, jsonify, request, make_response
from config import Config
from src.database.db import db
from src.routes.auth import auth_bp
from src.routes.student import student_bp
from src.routes.schedule import schedule_bp
from src.routes.payment import payment_bp
from src.routes.activity import activity_bp
from src.routes.notification import notification_bp
from src.routes.search import search_bp
import os
from src.services.mail_service import MailService

ALLOWED_ORIGINS = ['http://localhost:4200', 'http://127.0.0.1:4200']


def _cors_headers(response, origin):
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, x-access-token, Accept'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    MailService.init_app(app)
    db.init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(search_bp)

    # ── Uploads ───────────────────────────────────────────────────────
    basedir = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ── DB ────────────────────────────────────────────────────────────
    with app.app_context():
        from src.models.Notification import Notification  # noqa: F401
        db.create_all()

    # ── CORS global — intercepta ANTES que cualquier otra cosa ────────
    @app.before_request
    def handle_preflight():
        """Responde a OPTIONS inmediatamente con los headers correctos."""
        if request.method == 'OPTIONS':
            origin = request.headers.get('Origin', '')
            if origin in ALLOWED_ORIGINS:
                resp = make_response('', 204)
                return _cors_headers(resp, origin)
            return make_response('', 204)

    @app.after_request
    def add_cors_headers(response):
        """Agrega headers CORS a todas las respuestas reales."""
        origin = request.headers.get('Origin', '')
        if origin in ALLOWED_ORIGINS:
            _cors_headers(response, origin)
        return response

    # ── Health check ──────────────────────────────────────────────────
    @app.route('/ping')
    def ping():
        return jsonify({"status": "ok", "message": "Backend is running"}), 200

    @app.route('/')
    def index():
        return "¡El backend está funcionando!"

    return app
