from flask import Blueprint
from src.controllers.notification_controller import NotificationController
from src.middleware.jwt import jwt_required

notification_bp = Blueprint('notifications', __name__)


@notification_bp.route('/notifications', methods=['GET'])
@jwt_required
def get_notifications():
    return NotificationController.get_all()


@notification_bp.route('/notifications/read-all', methods=['PATCH'])
@jwt_required
def mark_all_as_read():
    return NotificationController.mark_all_as_read()


@notification_bp.route('/notifications/<int:notification_id>/read', methods=['PATCH'])
@jwt_required
def mark_as_read(notification_id):
    return NotificationController.mark_as_read(notification_id)


@notification_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required
def delete_notification(notification_id):
    return NotificationController.delete(notification_id)
