# src/controllers/auth_controller.py
from flask import current_app, jsonify
from src.models.password_reset_tokens import PasswordResetToken
import src.middleware.jwt as generate_token_module
from src.models.User import User
from src.database.db import db
from src.services.mail_service import MailService

class AuthController:
    def __init__(self, mail_service=None):
        self.mail_service = mail_service
        
    def register_user(self, nombre, apellido, username, email, password, rol='usuario', estado='activo'):
        """Registra un nuevo usuario"""
        email = email.lower() # Normalizar email a minúsculas
        # Verifica si el usuario ya existe
        if User.query.filter_by(email=email).first():
            raise ValueError("El email ya está registrado")
        if User.query.filter_by(username=username).first():
            raise ValueError("El nombre de usuario ya existe")
            
        new_user = User(
            nombre=nombre,
            apellido=apellido,
            username=username,
            email=email,
            rol=rol,
            estado=estado
        )
        new_user.set_password(password) # Usamos el método del modelo
        
        db.session.add(new_user)
        db.session.commit()

        # Enviar correo de bienvenida
        try:
            MailService.send_welcome_email(
                recipient_email=email,
                student_data={
                    'full_name': f"{nombre} {apellido}",
                    'email': email,
                    'username': username
                }
            )
        except Exception as e:
            current_app.logger.error(f"Error enviando correo de bienvenida a {email}: {e}")

        return new_user.serialize()

    def authenticate_user(self, identifier, password):
        # identifier puede ser email o username
        # Normalizar el identificador para la búsqueda
        if '@' in identifier:
            # Si el identificador parece un email, normalizarlo a minúsculas
            normalized_identifier = identifier.lower()
            user = User.query.filter_by(email=normalized_identifier).first()
        else:
            # Si no es un email, asumir que es un username y normalizarlo
            normalized_identifier = identifier.lower() # Aunque el username sea único, la comparación puede ser sensible a mayúsculas
            user = User.query.filter_by(username=normalized_identifier).first()

        if not user:
            current_app.logger.warning(f"Intento de login con identificador no registrado: {identifier}")
            return jsonify({"error": "Credenciales inválidas"}), 401

        if not user.check_password(password):
            current_app.logger.warning(f"Intento de login con contraseña incorrecta para: {identifier}")
            return jsonify({"error": "Credenciales inválidas"}), 401

        if user.estado == 'inactivo':
            current_app.logger.warning(f"Intento de login de usuario inactivo: {identifier}")
            return jsonify({"error": "Usuario inactivo"}), 401

        # Generar token, pasando el rol del usuario
        auth_token = generate_token_module.generate_token(user.id, user_data={'rol': user.rol})
        return jsonify({
            "message": "Login exitoso",
            "token": auth_token,
            "user_id": user.id,
            "rol": user.rol,
            "nombre": user.nombre,
            "apellido": user.apellido
        }), 200
        
    def initiate_password_reset(self, email):
        """Inicia el proceso de recuperación de contraseña"""
        # Validación del email
        if not email or not isinstance(email, str):
            raise ValueError("Email inválido")
            
        email = email.strip().lower()
            
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        if not user:
            current_app.logger.info(f"Intento de reset para email no registrado: {email}")
            return None
                
        expires_minutes = current_app.config.get('EXPIRES_TOKEN_EMAIL', 15)
            
        # Convertir a entero si es necesario
        if isinstance(expires_minutes, str):
            try:
                expires_minutes = int(expires_minutes)
            except ValueError:
                expires_minutes = 15
                    
        # Generar token
        token = PasswordResetToken.create_token(
            user.id,
            expires_minutes=expires_minutes
        )

        # Enviar correo
        if self.mail_service:
            reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
            self.mail_service.send_password_reset(
                email=email,
                token=token,
                reset_url=reset_url
            )
        
        return token
                
    def complete_password_reset(self, token, new_password):
        """Completa el proceso de recuperación de contraseña"""
        # Valida el token
        user_id = PasswordResetToken.validate_token(token)
        if not user_id:
            return False
            
        user = User.query.get(user_id)
        if not user:
            return False

        user.set_password(new_password) # Usamos el método del modelo
        db.session.commit()
        
        # Marca el token como usado
        PasswordResetToken.mark_as_used(token)
        
        return True
    
    def get_user_by_id(self, user_id):
        """Obtiene un usuario por su ID"""
        user = User.query.get(user_id)
        return user.serialize() if user else None
