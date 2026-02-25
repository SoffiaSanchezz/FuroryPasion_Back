from flask import Flask, send_from_directory # Import send_from_directory
from config import Config
from src.database.db import db
from src.routes.auth import auth_bp
from src.routes.student import student_bp
from src.routes.schedule import schedule_bp
from src.routes.payment import payment_bp
from src.routes.activity import activity_bp # Import activity_bp
from flask_cors import CORS
import os # Import os
from src.services.mail_service import MailService # Import MailService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    MailService.init_app(app) # Initialize MailService
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(activity_bp) # Register activity_bp

    # NEW: Serve uploaded files statically
    UPLOAD_DIR = os.path.join(app.root_path, 'uploads')
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR) # Ensure uploads directory exists

    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(UPLOAD_DIR, filename)
    # END NEW

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return "¡El backend está funcionando!"

    return app