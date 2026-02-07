from flask import Blueprint
from src.controllers.student_controller import StudentController
from src.middleware.jwt import jwt_required
from flask_cors import cross_origin

student_bp = Blueprint('students', __name__)

# Configuración CORS para todo el blueprint de estudiantes
# Permite solicitudes desde el frontend Angular (http://localhost:4200)
# Permite los métodos que se usarán en el CRUD y los encabezados necesarios (Content-Type, Authorization)
# supports_credentials=True es necesario para enviar cookies o encabezados de autorización en solicitudes CORS
student_cors_config = {
    "origins": "http://localhost:4200",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}

@student_bp.route('/students', methods=['POST'])
@cross_origin(**student_cors_config)
@jwt_required
def create_student_route():
    return StudentController.create_student()

@student_bp.route('/students', methods=['GET'])
@cross_origin(**student_cors_config)
@jwt_required
def get_students_route():
    return StudentController.get_students()

@student_bp.route('/students/<int:student_id>', methods=['GET'])
@cross_origin(**student_cors_config)
@jwt_required
def get_student_route(student_id):
    return StudentController.get_student(student_id)

@student_bp.route('/students/<int:student_id>', methods=['PUT'])
@cross_origin(**student_cors_config)
@jwt_required
def update_student_route(student_id):
    return StudentController.update_student(student_id)

@student_bp.route('/students/<int:student_id>', methods=['DELETE'])
@cross_origin(**student_cors_config)
@jwt_required
def delete_student_route(student_id):
    return StudentController.delete_student(student_id)