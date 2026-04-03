from src.database.db import db
from src.models.Payment import Payment
from src.models.Student import Student
from src.models.Installment import Installment
from datetime import datetime, date

class PaymentService:
    @staticmethod
    def _parse_date(date_str):
        if not date_str:
            return None
        # Limpiar posibles microsegundos excedentes o formatos variados de ISO
        date_str = date_str.replace('Z', '+00:00')
        formats = ['%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _validate_payment_data(data, is_new_payment=True):
        errors = {}
        
        # Validar campos requeridos
        required_fields = ['studentId', 'planAcquired', 'totalValue', 'amountPaid', 
                           'paymentMethod', 'startDate', 'endDate', 'receiptId']
        for field in required_fields:
            snake_case_field = ''.join(['_' + c.lower() if c.isupper() else c for c in field]).lstrip('_')
            if field not in data or data[field] is None or data[field] == '':
                errors[snake_case_field] = f"El campo {field} es obligatorio."
        
        # Validar valores numéricos
        if 'totalValue' in data and data['totalValue'] is not None:
            try:
                data['totalValue'] = float(data['totalValue'])
                if data['totalValue'] <= 0:
                    errors['total_value'] = 'El valor total debe ser positivo.'
            except (ValueError, TypeError):
                errors['total_value'] = 'El valor total debe ser un número válido.'
        
        if 'amountPaid' in data and data['amountPaid'] is not None:
            try:
                data['amountPaid'] = float(data['amountPaid'])
                if data['amountPaid'] < 0:
                    errors['amount_paid'] = 'El valor abonado no puede ser negativo.'
            except (ValueError, TypeError):
                errors['amount_paid'] = 'El valor abonado debe ser un número válido.'
        
        # Validar fechas usando el nuevo helper
        start_date = PaymentService._parse_date(data.get('startDate'))
        end_date = PaymentService._parse_date(data.get('endDate'))

        if not start_date and 'startDate' in data:
            errors['start_date'] = 'Formato de fecha de inicio inválido.'
        if not end_date and 'endDate' in data:
            errors['end_date'] = 'Formato de fecha de fin inválido.'

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
        
        if Payment.query.filter_by(receipt_id=data['receiptId']).first():
            return None, {"receiptId": "Ya existe un pago con este número de recibo."}

        start_date = PaymentService._parse_date(data['startDate'])
        end_date = PaymentService._parse_date(data['endDate'])

        new_payment = Payment(
            user_id=user_id,
            student_id=data['studentId'],
            plan_acquired=data['planAcquired'],
            total_value=data['totalValue'],
            amount_paid=data['amountPaid'],
            payment_method=data['paymentMethod'],
            start_date=start_date,
            end_date=end_date,
            receipt_id=data['receiptId']
        )
        
        db.session.add(new_payment)
        db.session.flush() # Obtener ID antes de commitear

        # Crear el primer abono automáticamente
        first_installment = Installment(
            payment_id=new_payment.id,
            amount=data['amountPaid'],
            payment_method=data['paymentMethod'],
            receipt_id=data['receiptId'],
            notes="Primer abono (pago inicial)"
        )
        db.session.add(first_installment)
        
        db.session.commit()

        # Crear notificación automática
        try:
            from src.services.notification_service import NotificationService
            NotificationService.notify_new_payment(user_id, new_payment)
        except Exception as e:
            from flask import current_app
            current_app.logger.warning(f"No se pudo crear notificación de pago: {e}")

        return new_payment, None

    @staticmethod
    def add_installment(user_id, payment_id, data):
        payment = PaymentService.get_payment_by_id(user_id, payment_id)
        if not payment:
            return None, {"general": "Pago no encontrado."}

        # Validaciones básicas de abono
        amount = float(data.get('amount', 0))
        if amount <= 0:
            return None, {"amount": "El monto del abono debe ser mayor a 0."}
        
        # Calcular saldo actual
        total_paid = sum(inst.amount for inst in payment.installments)
        pending = payment.total_value - total_paid
        
        if amount > pending:
            return None, {"amount": f"El abono (${amount}) supera el saldo pendiente (${pending})."}

        new_installment = Installment(
            payment_id=payment.id,
            amount=amount,
            payment_method=data.get('paymentMethod', 'Efectivo'),
            receipt_id=data.get('receiptId'),
            notes=data.get('notes', ''),
            date=datetime.utcnow()
        )
        
        db.session.add(new_installment)
        
        # Actualizar el campo redundante amount_paid en el padre para compatibilidad
        db.session.flush() # Sincronizar para que sum() detecte el nuevo registro
        payment.amount_paid = sum(inst.amount for inst in payment.installments)
        
        db.session.commit()
        return payment, None

    @staticmethod
    def get_all_payments(user_id):
        return Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()

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

        # Solo actualizamos metadatos, no montos (eso se hace por abonos)
        if 'planAcquired' in data: payment.plan_acquired = data['planAcquired']
        if 'startDate' in data: payment.start_date = PaymentService._parse_date(data['startDate'])
        if 'endDate' in data: payment.end_date = PaymentService._parse_date(data['endDate'])
        
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
