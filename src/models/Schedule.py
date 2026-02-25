from datetime import datetime
from src.database.db import db

class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    teacher_name = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.String(10), nullable=False) # Guardamos como HH:mm
    end_time = db.Column(db.String(10), nullable=False)   # Guardamos como HH:mm
    day = db.Column(db.String(20), nullable=False)        # Lunes, Martes, etc.
    status = db.Column(db.String(20), default='activo', nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='schedules', lazy=True)

    def __repr__(self):
        return f'<Schedule {self.name} - {self.day} {self.start_time}>'

    def serialize(self):
        return {
            "id": str(self.id), # El frontend espera string para el ID
            "name": self.name,
            "teacherName": self.teacher_name, # camelCase para el frontend
            "startTime": self.start_time,
            "endTime": self.end_time,
            "day": self.day,
            "status": self.status
        }
