from datetime import datetime
from src.database.db import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    
    plan_acquired = db.Column(db.String(50), nullable=False) # Mensual, Anual, etc.
    total_value = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) # Nequi, Daviplata, Efectivo, Transferencia, Otros
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    receipt_id = db.Column(db.String(100), unique=True, nullable=False)
    
    # Derivados, se pueden almacenar o calcular en el servicio/frontend
    # status = db.Column(db.String(20), nullable=False) # completed, partial
    # pending_balance = db.Column(db.Float, nullable=False)
    # plan_status = db.Column(db.String(20), nullable=False) # active, expiring_soon, expired
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='payments', lazy=True)
    student = db.relationship('Student', backref='payments', lazy=True)

    def __repr__(self):
        return f'<Payment {self.receipt_id} - Student:{self.student_id}>'

    def serialize(self):
        # Calcular status, pendingBalance y planStatus en el backend para consistencia
        total_value = self.total_value
        amount_paid = self.amount_paid
        pending_balance = total_value - amount_paid
        status = 'completed' if pending_balance <= 0 else 'partial'

        today = datetime.utcnow().date()
        plan_status = 'active'
        if self.end_date < today:
            plan_status = 'expired'
        elif (self.end_date - today).days <= 30: # 30 días para "expiring_soon"
            plan_status = 'expiring_soon'

        return {
            "id": str(self.id), # El frontend espera string para el ID
            "userId": str(self.user_id),
            "studentId": str(self.student_id),
            "studentName": self.student.full_name if self.student else "Desconocido", # Necesario para el frontend
            "planAcquired": self.plan_acquired,
            "totalValue": self.total_value,
            "amountPaid": self.amount_paid,
            "paymentMethod": self.payment_method,
            "startDate": self.start_date.isoformat(),
            "endDate": self.end_date.isoformat(),
            "receiptId": self.receipt_id,
            "status": status,
            "pendingBalance": pending_balance,
            "planStatus": plan_status,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }
