from flask import Blueprint
from src.controllers.payment_controller import PaymentController

payment_bp = Blueprint('payments', __name__)

@payment_bp.route('/payments', methods=['POST'])
def create_payment_route():
    return PaymentController.create_payment()

@payment_bp.route('/payments', methods=['GET'])
def get_all_payments_route():
    return PaymentController.get_all_payments()

@payment_bp.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment_route(payment_id):
    return PaymentController.get_payment(payment_id)

@payment_bp.route('/payments/<int:payment_id>/installments', methods=['POST', 'OPTIONS'])
def add_installment_route(payment_id):
    return PaymentController.add_installment(payment_id)

@payment_bp.route('/payments/student/<int:student_id>', methods=['GET'])
def get_payments_by_student_route(student_id):
    return PaymentController.get_payments_by_student(student_id)

@payment_bp.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment_route(payment_id):
    return PaymentController.update_payment(payment_id)

@payment_bp.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment_route(payment_id):
    return PaymentController.delete_payment(payment_id)
