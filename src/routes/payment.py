from flask import Blueprint
from src.controllers.payment_controller import PaymentController
from src.middleware.jwt import jwt_required
from flask_cors import cross_origin

payment_bp = Blueprint('payments', __name__)

# Configuración CORS genérica para las rutas de pagos
payment_cors_config = {
    "origins": "http://localhost:4200",
    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}

# --- Rutas para Pagos (Payments) ---
@payment_bp.route('/payments', methods=['POST'])
@cross_origin(**payment_cors_config)
@jwt_required
def create_payment_route():
    return PaymentController.create_payment()

@payment_bp.route('/payments', methods=['GET'])
@cross_origin(**payment_cors_config)
@jwt_required
def get_all_payments_route():
    return PaymentController.get_all_payments()

@payment_bp.route('/payments/<int:payment_id>', methods=['GET'])
@cross_origin(**payment_cors_config)
@jwt_required
def get_payment_route(payment_id):
    return PaymentController.get_payment(payment_id)

@payment_bp.route('/payments/student/<int:student_id>', methods=['GET'])
@cross_origin(**payment_cors_config)
@jwt_required
def get_payments_by_student_route(student_id):
    return PaymentController.get_payments_by_student(student_id)

@payment_bp.route('/payments/<int:payment_id>', methods=['PUT'])
@cross_origin(**payment_cors_config)
@jwt_required
def update_payment_route(payment_id):
    return PaymentController.update_payment(payment_id)

@payment_bp.route('/payments/<int:payment_id>', methods=['DELETE'])
@cross_origin(**payment_cors_config)
@jwt_required
def delete_payment_route(payment_id):
    return PaymentController.delete_payment(payment_id)
