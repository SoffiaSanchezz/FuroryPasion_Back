# furorypasion-back/src/models/Installment.py
from datetime import datetime
from src.database.db import db

class Installment(db.Model):
    __tablename__ = 'payment_installments'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id', ondelete='CASCADE'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    receipt_id = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def serialize(self):
        return {
            "id": str(self.id),
            "amount": self.amount,
            "paymentMethod": self.payment_method,
            "date": self.date.isoformat(),
            "receiptId": self.receipt_id,
            "notes": self.notes
        }
