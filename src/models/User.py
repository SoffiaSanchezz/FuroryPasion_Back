import bcrypt
from datetime import datetime
from src.database.db import db

class User(db.Model):
    """
    Modelo de datos para representar a un usuario en la base de datos.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(50), default='usuario', nullable=False) # admin / usuario / estudiante
    estado = db.Column(db.String(50), default='activo', nullable=False) # activo / inactivo
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        """
        Representación en string del objeto User.
        """
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        Hashea la contraseña usando bcrypt y la establece para el usuario.
        """
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """
        Verifica la contraseña ingresada con la contraseña hasheada almacenada.
        """
        if self.password and (self.password.startswith('$2b$') or self.password.startswith('$2a$')):
            return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
        return False

    def serialize(self):
        """
        Retorna un diccionario con los datos del usuario para ser convertido a JSON.
        No incluimos la contraseña por seguridad.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "username": self.username,
            "email": self.email,
            "rol": self.rol,
            "estado": self.estado,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
