from flask import Flask
from config import Config
from src.database.db import db
from src.routes.auth import auth_bp
from src.routes.student import student_bp # Importar el blueprint de estudiantes
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp) # Registrar el blueprint de estudiantes

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return "¡El backend está funcionando!"

    return app