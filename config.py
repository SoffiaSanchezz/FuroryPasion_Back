import os
import secrets
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv(override=True)

class Config:
    """
    Configuraciones para la aplicación Flask.
    """
    # Clave secreta: En producción debe venir de ENV. En desarrollo, generamos una segura si falta.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # Generar una clave segura de 32 bytes (64 caracteres hex) para HMAC-SHA256
        SECRET_KEY = secrets.token_hex(32)
        # Opcional: Advertir en consola si no es producción
        if os.environ.get('FLASK_ENV') != 'production':
            print(f"ADVERTENCIA: Usando SECRET_KEY generada automáticamente: {SECRET_KEY[:8]}...")
    
    # Configuración de la base de datos a partir de la variable de entorno
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Desactiva el seguimiento de modificaciones de SQLAlchemy para mejorar el rendimiento
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuraciones JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM') or 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES') or 1440) # En minutos (24 horas)

    # URL del frontend (para reset de contraseña, etc.)
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:4200'

    # URL base del backend (para construir URLs completas de archivos subidos)
    BASE_URL = os.environ.get('BACKEND_BASE_URL') or 'http://localhost:5000'

    # Configuraciones de Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.example.com' # Replace with your SMTP server
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@example.com' # Replace with your default sender
