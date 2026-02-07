from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Inicializa la instancia de SQLAlchemy globalmente
db = SQLAlchemy()

def init_db(app):
    """
    Inicializa la instancia de SQLAlchemy con la aplicación Flask.
    """
    # Configura la URI de la base de datos usando la variable de entorno DATABASE_URL
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/database")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Desactiva el seguimiento de modificaciones de SQLAlchemy
    db.init_app(app) # Vincula la instancia de SQLAlchemy a la aplicación Flask
    logger.info("Base de datos inicializada con la aplicación Flask.")
    
    # Importa los modelos aquí para asegurar que estén registrados con SQLAlchemy
    # Esto ayuda a prevenir importaciones circulares y asegura que SQLAlchemy conozca los modelos
    from src.models.User import User
    from src.models.password_reset_tokens import PasswordResetToken
    # Puedes añadir aquí otras importaciones de modelos si es necesario
