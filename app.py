from flask import Flask, send_from_directory, jsonify
from config import Config
from src.database.db import db
from src.routes.auth import auth_bp
from src.routes.student import student_bp
from src.routes.schedule import schedule_bp
from src.routes.payment import payment_bp
from src.routes.activity import activity_bp
from flask_cors import CORS
import os
from src.services.mail_service import MailService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configuración global de CORS reforzada
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:4200", "http://127.0.0.1:4200"],
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "x-access-token"]
    }}, supports_credentials=True)
    
    MailService.init_app(app)
    db.init_app(app)
    
    # Registro de Blueprints con prefijos correctos
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(activity_bp)

    # Configuración de subida de archivos con ruta absoluta
    basedir = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    with app.app_context():
        db.create_all()

    @app.route('/ping')
    def ping():
        return jsonify({"status": "ok", "message": "Backend is running"}), 200

    @app.route('/')
    def index():
        return "¡El backend está funcionando!"

    return app
