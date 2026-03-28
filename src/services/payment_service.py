from src.database.db import db
from src.models.Payment import Payment
from src.models.Student import Student
from datetime import datetime, date

class PaymentService:
    @staticmethod
    def _validate_payment_data(data, is_new_payment=True):
        errors = {}
        
        # Validar campos requeridos
        required_fields = ['studentId', 'planAcquired', 'totalValue', 'amountPaid', 
                           'paymentMethod', 'startDate', 'endDate', 'receiptId']
        for field in required_fields:
            # Convertir de camelCase a snake_case para usar los nombres de las claves de la BBDD
            snake_case_field = ''.join(['_' + c.lower() if c.isupper() else c for c in field]).lstrip('_')
            if field not in data or not data[field]:
                errors[snake_case_field] = f"El campo {field} es obligatorio."
        
        # Validar valores numéricos
        if 'totalValue' in data and data['totalValue'] is not None:
            try:
                data['totalValue'] = float(data['totalValue'])
                if data['totalValue'] <= 0:
                    errors['total_value'] = 'El valor total debe ser positivo.'
            except ValueError:
                errors['total_value'] = 'El valor total debe ser un número válido.'
        
        if 'amountPaid' in data and data['amountPaid'] is not None:
            try:
                data['amountPaid'] = float(data['amountPaid'])
                if data['amountPaid'] < 0:
                    errors['amount_paid'] = 'El valor abonado no puede ser negativo.'
                elif data['amountPaid'] > data.get('totalValue', 0):
                    errors['amount_paid'] = 'El valor abonado no puede ser mayor que el valor total.'
            except ValueError:
                errors['amount_paid'] = 'El valor abonado debe ser un número válido.'
        
        # Validar fechas
        start_date = None
        end_date = None
        if 'startDate' in data and data['startDate']:
            try:
                start_date = datetime.strptime(data['startDate'], '%Y-%m-%dT%H:%M:%S.%fZ').date() # From ISO string
            except ValueError:
                try:
                    start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date() # From 'YYYY-MM-DD'
                except ValueError:
                    errors['start_date'] = 'Formato de fecha de inicio inválido (esperado YYYY-MM-DD o ISO string).'
        
        if 'endDate' in data and data['endDate']:
            try:
                end_date = datetime.strptime(data['endDate'], '%Y-%m-%dT%H:%M:%S.%fZ').date() # From ISO string
            except ValueError:
                try:
                    end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date() # From 'YYYY-MM-DD'
                except ValueError:
                    errors['end_date'] = 'Formato de fecha de fin inválido (esperado YYYY-MM-DD o ISO string).'

        if start_date and end_date:
            if start_date >= end_date:
                errors['end_date'] = 'La fecha de fin debe ser posterior a la fecha de inicio.'
        
        return errors

    @staticmethod
    def create_payment(user_id, data):
        errors = PaymentService._validate_payment_data(data)
        if errors:
            return None, errors

        student = Student.query.get(data['studentId'])
        if not student:
            return None, {"studentId": "Estudiante no encontrado."}
        
        # Verificar unicidad del receipt_id
        if Payment.query.filter_by(receipt_id=data['receiptId']).first():
            return None, {"receiptId": "Ya existe un pago con este número de recibo."}

        new_payment = Payment(
            user_id=user_id,
            student_id=data['studentId'],
            plan_acquired=data['planAcquired'],
            total_value=data['totalValue'],
            amount_paid=data['amountPaid'],
            payment_method=data['paymentMethod'],
            start_date=datetime.strptime(data['startDate'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
            end_date=datetime.strptime(data['endDate'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
            receipt_id=data['receiptId']
        )
        
        db.session.add(new_payment)
        db.session.commit()
        return new_payment, None

    @staticmethod
    def get_all_payments(user_id):
        # Filtra pagos por el user_id del administrador
        return Payment.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_payment_by_id(user_id, payment_id):
        return Payment.query.filter_by(user_id=user_id, id=payment_id).first()
    
    @staticmethod
    def get_payments_by_student(user_id, student_id):
        return Payment.query.filter_by(user_id=user_id, student_id=student_id).all()

    @staticmethod
    def update_payment(user_id, payment_id, data):
        payment = PaymentService.get_payment_by_id(user_id, payment_id)
        if not payment:
            return None, {"general": "Pago no encontrado o no autorizado."}

        errors = PaymentService._validate_payment_data(data, is_new_payment=False)
        if errors:
            return None, errors
        
        # Verificar unicidad del receipt_id si cambia
        if 'receiptId' in data and data['receiptId'] != payment.receipt_id:
            if Payment.query.filter_by(receipt_id=data['receiptId']).first():
                return None, {"receiptId": "Ya existe otro pago con este número de recibo."}

        payment.plan_acquired = data.get('planAcquired', payment.plan_acquired)
        payment.total_value = data.get('totalValue', payment.total_value)
        payment.amount_paid = data.get('amountPaid', payment.amount_paid)
        payment.payment_method = data.get('paymentMethod', payment.payment_method)
        
        if 'startDate' in data:
            payment.start_date = datetime.strptime(data['startDate'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        if 'endDate' in data:
            payment.end_date = datetime.strptime(data['endDate'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
            
        payment.receipt_id = data.get('receiptId', payment.receipt_id)
        
        db.session.commit()
        return payment, None

    @staticmethod
    def delete_payment(user_id, payment_id):
        payment = PaymentService.get_payment_by_id(user_id, payment_id)
        if not payment:
            return False, "Pago no encontrado o no autorizado."
        
        db.session.delete(payment)
        db.session.commit()
        return True, None
