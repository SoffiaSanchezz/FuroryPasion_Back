from flask import Blueprint
from src.controllers.student_controller import StudentController
from src.middleware.jwt import jwt_required
from flask_cors import cross_origin

student_bp = Blueprint('students', __name__)

@student_bp.route('/students/regulation', methods=['GET'])
@jwt_required
def get_regulation_route():
    return StudentController.get_regulation()

@student_bp.route('/students/affiliate', methods=['POST'])
@jwt_required
def affiliate_student_route():
    return StudentController.create_student()

@student_bp.route('/students', methods=['POST'])
@jwt_required
def create_student_route():
    return StudentController.create_student()

@student_bp.route('/students', methods=['GET'])
@jwt_required
def get_students_route():
    return StudentController.get_students()

@student_bp.route('/students/<int:student_id>', methods=['GET'])
@jwt_required
def get_student_route(student_id):
    return StudentController.get_student(student_id)

@student_bp.route('/students/<int:student_id>/guardian', methods=['GET', 'OPTIONS'])
@jwt_required
def get_guardian_route(student_id):
    return StudentController.get_guardian(student_id)

@student_bp.route('/students/<int:student_id>', methods=['PUT'])
@jwt_required
def update_student_route(student_id):
    return StudentController.update_student(student_id)

@student_bp.route('/students/<int:student_id>', methods=['DELETE'])
@jwt_required
def delete_student_route(student_id):
    return StudentController.delete_student(student_id)

@student_bp.route('/students/<int:student_id>/status', methods=['PATCH'])
@jwt_required
def toggle_student_status_route(student_id):
    return StudentController.toggle_student_status(student_id)