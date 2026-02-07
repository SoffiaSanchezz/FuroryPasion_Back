from datetime import datetime
from src.database.db import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Datos del estudiante
    full_name = db.Column(db.String(200), nullable=False)
    document_id = db.Column(db.String(50), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True) # Puede ser nulo si es menor y no tiene email
    phone = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    photo_path = db.Column(db.String(255), nullable=True) # Ruta de la foto del estudiante
    signature_path = db.Column(db.String(255), nullable=True) # Ruta de la firma digital
    is_minor = db.Column(db.Boolean, default=False, nullable=False) # Para indicar si es menor de edad
    
    # Datos del acudiente (si aplica)
    guardian_full_name = db.Column(db.String(200), nullable=True)
    guardian_document_id = db.Column(db.String(50), nullable=True)
    guardian_phone = db.Column(db.String(50), nullable=True)
    guardian_relationship = db.Column(db.String(50), nullable=True) # Ej: 'Padre', 'Madre', 'Tutor'

    status = db.Column(db.String(50), default='activo', nullable=False) # activo / inactivo (para soft delete)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='students', lazy=True)

    def __repr__(self):
        return f'<Student {self.full_name} ({self.document_id})>'

    def serialize(self):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "document_id": self.document_id,
            "date_of_birth": self.date_of_birth.isoformat(),
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "photo_path": self.photo_path,
            "signature_path": self.signature_path, # Include new field
            "is_minor": self.is_minor,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        if self.is_minor:
            data.update({
                "guardian_full_name": self.guardian_full_name,
                "guardian_document_id": self.guardian_document_id,
                "guardian_phone": self.guardian_phone,
                "guardian_relationship": self.guardian_relationship
            })
        return data

    def soft_delete(self):
        self.status = 'inactivo'
        db.session.commit()
        return self