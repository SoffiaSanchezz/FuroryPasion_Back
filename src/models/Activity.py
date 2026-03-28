from datetime import datetime
from src.database.db import db
import json # Importar json para manejar la lista de emails

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.String(10), nullable=False) # HH:mm
    image_path = db.Column(db.String(255), nullable=True) # Path to uploaded image
    invited_emails = db.Column(db.Text, nullable=True) # Stores JSON array of emails
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='activities', lazy=True)

    def __repr__(self):
        return f'<Activity {self.title} on {self.event_date} at {self.event_time}>'

    def serialize(self):
        return {
            "id": str(self.id),
            "userId": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "eventDate": self.event_date.isoformat(),
            "eventTime": self.event_time,
            "imagePath": self.image_path,
            "invitedEmails": json.loads(self.invited_emails) if self.invited_emails else [],
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }
