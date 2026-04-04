from flask import Blueprint, request, make_response
from src.controllers.payment_controller import PaymentController
from src.middleware.jwt import jwt_required

payment_bp = Blueprint('payments', __name__)


def _cors_preflight():
    response = make_response('', 204)
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:4200')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, x-access-token, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response


@payment_bp.route('/payments', methods=['POST', 'OPTIONS'])
@jwt_required
def create_payment_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return PaymentController.create_payment()

@payment_bp.route('/payments', methods=['GET', 'OPTIONS'])
@jwt_required
def get_all_payments_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return PaymentController.get_all_payments()

@payment_bp.route('/payments/<int:payment_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_payment_route(payment_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return PaymentController.get_payment(payment_id)

@payment_bp.route('/payments/<int:payment_id>/installments', methods=['POST', 'OPTIONS'])
@jwt_required
def add_installment_route(payment_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return PaymentController.add_installment(payment_id)

@payment_bp.route('/payments/student/<int:student_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_payments_by_student_route(student_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return PaymentController.get_payments_by_student(student_id)

@payment_bp.route('/payments/<int:payment_id>', methods=['PUT', 'OPTIONS'])
@jwt_required
def update_payment_route(payment_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return PaymentController.update_payment(payment_id)

@payment_bp.route('/payments/<int:payment_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required
def delete_payment_route(payment_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return PaymentController.delete_payment(payment_id)
