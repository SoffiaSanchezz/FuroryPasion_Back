from flask_mail import Mail, Message
from flask import current_app, render_template
import os
from datetime import datetime # Import datetime

mail = Mail()

class MailService:
    @staticmethod
    def init_app(app):
        mail.init_app(app)

    @staticmethod
    def send_invitation_email(recipient_emails, activity_data, image_attachment=None):
        if not recipient_emails:
            current_app.logger.warning("No recipient emails provided for invitation.")
            return False

        if not isinstance(recipient_emails, list):
            recipient_emails = [recipient_emails] # Ensure it's a list

        try:
            with current_app.app_context():
                msg = Message(
                    subject=f"Invitación a Actividad: {activity_data['title']}",
                    sender=current_app.config['MAIL_DEFAULT_SENDER'],
                    recipients=recipient_emails
                )
                # Render HTML template for the email body
                msg.html = render_template(
                    'emails/activity_invitation.html',
                    activity=activity_data,
                    base_url=current_app.config['BASE_URL'],
                    current_year=datetime.utcnow().year # Pass current year to template
                )

                # Attach image if provided
                if image_attachment and os.path.exists(image_attachment):
                    with current_app.open_resource(image_attachment) as fp:
                        msg.attach(
                            filename=os.path.basename(image_attachment),
                            content_type="image/png", # Assuming PNG, adjust if other types are allowed
                            data=fp.read(),
                            disposition="inline", # Display inline in email
                            headers=[["Content-ID", f"<{os.path.basename(image_attachment)}>"]] # For inline embedding
                        )
                
                mail.send(msg)
                current_app.logger.info(f"Invitation email sent for '{activity_data['title']}' to {recipient_emails}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending invitation email: {e}", exc_info=True)
            return False