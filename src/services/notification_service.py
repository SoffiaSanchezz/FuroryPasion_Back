from src.database.db import db
from src.models.Notification import Notification
from src.models.Student import Student
from src.models.Payment import Payment
from src.models.Activity import Activity
from datetime import datetime


class NotificationService:

    @staticmethod
    def get_notifications(user_id: int) -> list:
        """Devuelve todas las notificaciones del usuario, más recientes primero."""
        return (
            Notification.query
            .filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_as_read(user_id: int, notification_id: int):
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if not notif:
            return None, "Notificación no encontrada"
        notif.is_read = True
        db.session.commit()
        return notif, None

    @staticmethod
    def mark_all_as_read(user_id: int):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
        db.session.commit()

    @staticmethod
    def delete_notification(user_id: int, notification_id: int):
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if not notif:
            return False, "Notificación no encontrada"
        db.session.delete(notif)
        db.session.commit()
        return True, None

    # ------------------------------------------------------------------ #
    #  Helpers para crear notificaciones desde otros servicios            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def create(user_id: int, type: str, icon: str, title: str,
               description: str, source_type: str = None, source_id: int = None):
        notif = Notification(
            user_id=user_id,
            type=type,
            icon=icon,
            title=title,
            description=description,
            source_type=source_type,
            source_id=source_id
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    @staticmethod
    def notify_new_student(user_id: int, student: Student):
        # Evitar duplicados
        existing = Notification.query.filter_by(
            user_id=user_id, source_type='student', source_id=student.id
        ).first()
        if existing:
            return
        NotificationService.create(
            user_id=user_id,
            type='student',
            icon='bi-person-plus-fill',
            title='Nuevo Estudiante Registrado',
            description=f'{student.full_name} se ha unido a la academia.',
            source_type='student',
            source_id=student.id
        )

    @staticmethod
    def notify_new_payment(user_id: int, payment: Payment):
        existing = Notification.query.filter_by(
            user_id=user_id, source_type='payment', source_id=payment.id
        ).first()
        if existing:
            return
        amount = payment.amount_paid
        NotificationService.create(
            user_id=user_id,
            type='payment',
            icon='bi-cash-stack',
            title='Pago Recibido',
            description=f'Recibo #{payment.receipt_id} procesado exitosamente (${amount:,.2f}).',
            source_type='payment',
            source_id=payment.id
        )

    @staticmethod
    def notify_new_activity(user_id: int, activity: Activity):
        existing = Notification.query.filter_by(
            user_id=user_id, source_type='activity', source_id=activity.id
        ).first()
        if existing:
            return
        NotificationService.create(
            user_id=user_id,
            type='class',
            icon='bi-calendar-plus',
            title='Nueva Actividad Creada',
            description=f'Se ha creado la actividad "{activity.title}".',
            source_type='activity',
            source_id=activity.id
        )

    @staticmethod
    def sync_notifications(user_id: int):
        """
        Sincroniza notificaciones desde los datos existentes.
        Útil para poblar la tabla la primera vez o en cada login.
        """
        students = Student.query.filter_by(user_id=user_id).order_by(
            Student.created_at.desc()).limit(10).all()
        for s in students:
            NotificationService.notify_new_student(user_id, s)

        payments = Payment.query.filter_by(user_id=user_id).order_by(
            Payment.created_at.desc()).limit(10).all()
        for p in payments:
            NotificationService.notify_new_payment(user_id, p)

        activities = Activity.query.filter_by(user_id=user_id).order_by(
            Activity.created_at.desc()).limit(10).all()
        for a in activities:
            NotificationService.notify_new_activity(user_id, a)
