from flask import Blueprint, request, jsonify, g
from src.controllers.auth import AuthController
from src.middleware.jwt import jwt_required

auth_bp = Blueprint('auth', __name__)
auth_controller = AuthController()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        user_data = {
            'nombre': data.get('nombre'),
            'apellido': data.get('apellido'),
            'username': data.get('username'),
            'email': data.get('email'),
            'password': data.get('password'),
            'rol': data.get('rol', 'estudiante'),
            'estado': data.get('estado', 'activo')
        }
        
        if not all(user_data.get(field) for field in ['nombre', 'username', 'email', 'password']):
            return jsonify({"error": "Faltan campos obligatorios para el registro"}), 400

        user = auth_controller.register_user(**user_data)
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor al registrar usuario"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')
    password = data.get('password')
    
    if not identifier or not password:
        return jsonify({"error": "Identificador y contraseña requeridos"}), 400

    response, status_code = auth_controller.authenticate_user(identifier, password)
    return response, status_code

@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    try:
        user = auth_controller.get_user_by_id(g.current_user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener datos del usuario"}), 500

@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email requerido"}), 400
    try:
        auth_controller.initiate_password_reset(email)
        return jsonify({"message": "Si tu email está registrado, recibirás un enlace"}), 200
    except Exception as e:
        return jsonify({"error": "Error al iniciar el reset"}), 500

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    if not token or not new_password:
        return jsonify({"error": "Token y nueva contraseña requeridos"}), 400
    try:
        if auth_controller.complete_password_reset(token, new_password):
            return jsonify({"message": "Contraseña restablecida correctamente"}), 200
        else:
            return jsonify({"error": "Token inválido o expirado"}), 400
    except Exception as e:
        return jsonify({"error": "Error al restablecer la contraseña"}), 500
