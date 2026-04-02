from flask import request, jsonify, g
from src.services.payment_service import PaymentService

class PaymentController:
    @staticmethod
    def create_payment():
        data = request.get_json()
        user_id = g.current_user_id

        payment, errors = PaymentService.create_payment(user_id, data)
        if errors:
            return jsonify({"errors": errors}), 400
        return jsonify(payment.serialize()), 201

    @staticmethod
    def get_all_payments():
        user_id = g.current_user_id
        payments = PaymentService.get_all_payments(user_id)
        return jsonify([payment.serialize() for payment in payments]), 200

    @staticmethod
    def get_payment(payment_id):
        user_id = g.current_user_id
        payment = PaymentService.get_payment_by_id(user_id, payment_id)
        if not payment:
            return jsonify({"error": "Pago no encontrado o no autorizado."}), 404
        return jsonify(payment.serialize()), 200
    
    @staticmethod
    def add_installment(payment_id):
        data = request.get_json()
        user_id = g.current_user_id
        
        payment, errors = PaymentService.add_installment(user_id, payment_id, data)
        if errors:
            return jsonify({"errors": errors}), 400
        return jsonify(payment.serialize()), 201
    
    @staticmethod
    def get_payments_by_student(student_id):
        user_id = g.current_user_id
        payments = PaymentService.get_payments_by_student(user_id, student_id)
        return jsonify([payment.serialize() for payment in payments]), 200

    @staticmethod
    def update_payment(payment_id):
        data = request.get_json()
        user_id = g.current_user_id

        payment, errors = PaymentService.update_payment(user_id, payment_id, data)
        if errors:
            if "general" in errors:
                return jsonify({"error": errors["general"]}), 404
            return jsonify({"errors": errors}), 400
        return jsonify(payment.serialize()), 200

    @staticmethod
    def delete_payment(payment_id):
        user_id = g.current_user_id
        success, error = PaymentService.delete_payment(user_id, payment_id)
        if not success:
            return jsonify({"error": error}), 404
        return jsonify({"message": "Pago eliminado exitosamente."}), 200
