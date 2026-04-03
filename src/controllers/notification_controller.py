from flask import jsonify, g
from src.services.notification_service import NotificationService
from src.models.Notification import Notification


class NotificationController:

    @staticmethod
    def get_all():
        user_id = g.current_user_id

        # Solo sincroniza si el usuario no tiene notificaciones aún (primera vez)
        has_any = Notification.query.filter_by(user_id=user_id).first()
        if not has_any:
            NotificationService.sync_notifications(user_id)

        notifications = NotificationService.get_notifications(user_id)
        unread = NotificationService.get_unread_count(user_id)
        return jsonify({
            "notifications": [n.serialize() for n in notifications],
            "unreadCount": unread
        }), 200

    @staticmethod
    def mark_as_read(notification_id):
        user_id = g.current_user_id
        notif, error = NotificationService.mark_as_read(user_id, notification_id)
        if error:
            return jsonify({"error": error}), 404
        return jsonify(notif.serialize()), 200

    @staticmethod
    def mark_all_as_read():
        user_id = g.current_user_id
        NotificationService.mark_all_as_read(user_id)
        return jsonify({"message": "Todas las notificaciones marcadas como leídas"}), 200

    @staticmethod
    def delete(notification_id):
        user_id = g.current_user_id
        success, error = NotificationService.delete_notification(user_id, notification_id)
        if not success:
            return jsonify({"error": error}), 404
        return jsonify({"message": "Notificación eliminada"}), 200
