import secrets
from datetime import datetime, timedelta
from flask import current_app
from src.database.db import db
from sqlalchemy import ForeignKey

class PasswordResetToken(db.Model):
    """
    Modelo de datos para representar un token de restablecimiento de contraseña en la base de datos.
    """
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create_token(cls, user_id, expires_minutes=15):
        """Crea y almacena un token de restablecimiento de contraseña."""
        token_str = secrets.token_urlsafe(32) # Genera un token seguro
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

        new_token = cls(
            user_id=user_id,
            token=token_str,
            expires_at=expires_at,
            used=False
        )
        db.session.add(new_token)
        db.session.commit()
        return token_str

    @classmethod
    def validate_token(cls, token_str):
        """Valida un token de restablecimiento de contraseña."""
        token_obj = cls.query.filter_by(token=token_str, used=False).first()
        if token_obj and token_obj.expires_at > datetime.utcnow():
            return token_obj.user_id
        return None

    @classmethod
    def mark_as_used(cls, token_str):
        """Marca un token de restablecimiento de contraseña como usado."""
        token_obj = cls.query.filter_by(token=token_str).first()
        if token_obj:
            token_obj.used = True
            db.session.commit()
            return True
        return False
