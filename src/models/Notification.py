from datetime import datetime
from src.database.db import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    type = db.Column(db.String(50), nullable=False)   # student | payment | class | system
    icon = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    # Referencia opcional al objeto que originó la notificación
    source_type = db.Column(db.String(50), nullable=True)   # 'student' | 'payment' | 'activity'
    source_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='notifications', lazy=True)

    def serialize(self):
        return {
            "id": str(self.id),
            "type": self.type,
            "icon": self.icon,
            "title": self.title,
            "description": self.description,
            "isRead": self.is_read,
            "sourceType": self.source_type,
            "sourceId": self.source_id,
            "createdAt": self.created_at.isoformat()
        }
