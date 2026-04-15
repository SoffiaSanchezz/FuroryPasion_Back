from flask import jsonify, g, current_app
from src.services.notification_service import NotificationService


class NotificationController:

    @staticmethod
    def get_all():
        user_id = g.current_user_id

        # Sincroniza siempre — idempotente por source_type+source_id
        # Detecta nuevos pagos/estudiantes/actividades sin notificación aún
        try:
            NotificationService.sync_notifications(user_id)
        except Exception as e:
            current_app.logger.error(f"sync_notifications falló para user {user_id}: {e}")

        # Solo devuelve NO leídas — las leídas no reaparecen
        notifications = NotificationService.get_notifications(user_id)
        unread = len(notifications)

        current_app.logger.debug(f"GET /notifications user={user_id} → {unread} no leídas")

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
