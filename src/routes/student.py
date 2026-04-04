from flask import Blueprint, request, make_response
from src.controllers.student_controller import StudentController
from src.middleware.jwt import jwt_required

student_bp = Blueprint('students', __name__)


def _cors_preflight():
    """Responde el preflight OPTIONS con los headers CORS correctos."""
    response = make_response('', 204)
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:4200')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, x-access-token, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response


@student_bp.route('/students/regulation', methods=['GET', 'OPTIONS'])
@jwt_required
def get_regulation_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return StudentController.get_regulation()


@student_bp.route('/students/check-document/<string:document_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def check_document_route(document_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return StudentController.check_document(document_id)


@student_bp.route('/students/verify-photo', methods=['POST', 'OPTIONS'])
@jwt_required
def verify_photo_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return StudentController.verify_photo()


@student_bp.route('/students/affiliate', methods=['POST', 'OPTIONS'])
@jwt_required
def affiliate_student_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return StudentController.create_student()


@student_bp.route('/students', methods=['GET', 'POST', 'OPTIONS'])
@jwt_required
def students_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    if request.method == 'GET':
        return StudentController.get_students()
    return StudentController.create_student()


@student_bp.route('/students/<int:student_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
@jwt_required
def student_detail_route(student_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    if request.method == 'GET':
        return StudentController.get_student(student_id)
    if request.method == 'PUT':
        return StudentController.update_student(student_id)
    return StudentController.delete_student(student_id)


@student_bp.route('/students/<int:student_id>/guardian', methods=['GET', 'OPTIONS'])
@jwt_required
def get_guardian_route(student_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return StudentController.get_guardian(student_id)


@student_bp.route('/students/<int:student_id>/status', methods=['PATCH', 'OPTIONS'])
@jwt_required
def toggle_student_status_route(student_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return StudentController.toggle_student_status(student_id)
