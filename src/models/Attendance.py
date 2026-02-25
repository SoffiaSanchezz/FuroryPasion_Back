from datetime import datetime
from src.database.db import db

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id', ondelete='CASCADE'), nullable=False)
    
    arrival_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False) # presente, tarde, ausente
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship('Student', backref='attendances', lazy=True)
    schedule = db.relationship('Schedule', backref='attendances', lazy=True)

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Schedule:{self.schedule_id}>'

    def serialize(self):
        return {
            "id": str(self.id),
            "studentId": str(self.student_id),
            "studentName": self.student.full_name if self.student else "Desconocido",
            "classScheduleId": str(self.schedule_id),
            "classScheduleName": self.schedule.name if self.schedule else "Clase eliminada",
            "arrivalTime": self.arrival_time.isoformat(),
            "status": self.status,
            "notes": self.notes
        }
