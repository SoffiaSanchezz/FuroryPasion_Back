from src.database.db import db
from src.models.Activity import Activity
from src.models.User import User
from src.utils.file_upload_helper import FileUploadHelper
from datetime import datetime, date
import json
import re
from src.services.mail_service import MailService # Import MailService

class ActivityService:
    @staticmethod
    def _validate_activity_data(data, is_new_activity=True):
        errors = {}

        required_fields = ['title', 'eventDate', 'eventTime']
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f"El campo {field} es obligatorio."
        
        if 'title' in data and len(data['title']) > 255:
            errors['title'] = "El título no puede exceder los 255 caracteres."

        if 'eventDate' in data and data['eventDate']:
            try:
                # Intentar parsear como YYYY-MM-DD
                data['eventDate'] = datetime.strptime(data['eventDate'], '%Y-%m-%d').date()
            except ValueError:
                errors['eventDate'] = "Formato de fecha de evento inválido (esperado YYYY-MM-DD)."
        
        if 'eventTime' in data and data['eventTime']:
            try:
                # Validar formato HH:mm
                datetime.strptime(data['eventTime'], '%H:%M')
            except ValueError:
                errors['eventTime'] = "Formato de hora de evento inválido (esperado HH:mm)."

        if 'invitedEmails' in data and data['invitedEmails']:
            if not isinstance(data['invitedEmails'], list):
                errors['invitedEmails'] = "La lista de correos electrónicos invitados debe ser un array."
            else:
                invalid_emails = [email for email in data['invitedEmails'] if not re.match(r"[^@]+@[^@]+\.[^@]+", email)]
                if invalid_emails:
                    errors['invitedEmails'] = f"Los siguientes correos electrónicos son inválidos: {', '.join(invalid_emails)}"
        
        return errors

    @staticmethod
    def create_activity(user_id, data, image_file=None):
        errors = ActivityService._validate_activity_data(data)
        if errors:
            return None, errors

        # Handle image upload
        image_path = None
        if image_file:
            image_path, upload_error = FileUploadHelper.save_photo(image_file, "activity_images")
            if upload_error:
                errors['imagePath'] = upload_error
                return None, errors

        new_activity = Activity(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            event_date=data['eventDate'],
            event_time=data['eventTime'],
            image_path=image_path,
            invited_emails=json.dumps(data.get('invitedEmails', [])) # Store as JSON string
        )

        db.session.add(new_activity)
        db.session.commit()

        # Crear notificación automática
        try:
            from src.services.notification_service import NotificationService
            NotificationService.notify_new_activity(user_id, new_activity)
        except Exception as e:
            from flask import current_app
            current_app.logger.warning(f"No se pudo crear notificación de actividad: {e}")

        # Send invitations if there are recipients
        if new_activity.invited_emails:
            recipient_emails = json.loads(new_activity.invited_emails)
            activity_data = new_activity.serialize() # Get serialized data for email template
            # Get absolute path for image attachment if exists
            image_attachment_path = None
            if new_activity.image_path:
                from flask import current_app # Import here to avoid circular dependency
                import os # Import os here as well
                image_attachment_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_activity.image_path)
            
            MailService.send_invitation_email(recipient_emails, activity_data, image_attachment_path)
        
        return new_activity, None

    @staticmethod
    def get_all_activities(user_id):
        return Activity.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_activity_by_id(user_id, activity_id):
        return Activity.query.filter_by(user_id=user_id, id=activity_id).first()

    @staticmethod
    def update_activity(user_id, activity_id, data, image_file=None):
        activity = ActivityService.get_activity_by_id(user_id, activity_id)
        if not activity:
            return None, {"general": "Actividad no encontrada o no autorizada."}

        errors = ActivityService._validate_activity_data(data, is_new_activity=False)
        if errors:
            return None, errors
        
        # Handle image update/deletion
        if image_file:
            # Delete old image if exists
            if activity.image_path:
                FileUploadHelper.delete_file(activity.image_path)
            image_path, upload_error = FileUploadHelper.save_photo(image_file, "activity_images")
            if upload_error:
                errors['imagePath'] = upload_error
                return None, errors
            activity.image_path = image_path
        elif 'imagePath' in data and data['imagePath'] is None: # Allow explicitly setting to null
            if activity.image_path:
                FileUploadHelper.delete_file(activity.image_path)
            activity.image_path = None


        activity.title = data.get('title', activity.title)
        activity.description = data.get('description', activity.description)
        activity.event_date = data.get('eventDate', activity.event_date)
        activity.event_time = data.get('eventTime', activity.event_time)
        activity.invited_emails = json.dumps(data.get('invitedEmails', []))
        
        db.session.commit()

        # Resend invitations if invited_emails updated
        if activity.invited_emails:
            recipient_emails = json.loads(activity.invited_emails)
            activity_data = activity.serialize()
            image_attachment_path = None
            if activity.image_path:
                from flask import current_app
                import os # Import os here as well
                image_attachment_path = os.path.join(current_app.config['UPLOAD_FOLDER'], activity.image_path)
            MailService.send_invitation_email(recipient_emails, activity_data, image_attachment_path)
        
        return activity, None

    @staticmethod
    def delete_activity(user_id, activity_id):
        activity = ActivityService.get_activity_by_id(user_id, activity_id)
        if not activity:
            return False, "Actividad no encontrada o no autorizada."
        
        # Delete associated image file
        if activity.image_path:
            FileUploadHelper.delete_file(activity.image_path)

        db.session.delete(activity)
        db.session.commit()
        return True, None

    # TODO: Implement actual email sending functionality
    @staticmethod
    def send_invitations(activity):
        # Placeholder for email sending
        print(f"Sending invitations for activity: {activity.title} to {activity.invited_emails}")
        pass
