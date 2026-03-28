from flask import Blueprint
from src.controllers.activity_controller import ActivityController
from src.middleware.jwt import jwt_required
from flask_cors import cross_origin

activity_bp = Blueprint('activities', __name__)

# Configuración CORS genérica para las rutas de actividades
activity_cors_config = {
    "origins": "http://localhost:4200",
    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}

# --- Rutas para Actividades (Activities) ---
@activity_bp.route('/activities', methods=['POST'])
@cross_origin(**activity_cors_config)
@jwt_required
def create_activity_route():
    return ActivityController.create_activity()

@activity_bp.route('/activities', methods=['GET'])
@cross_origin(**activity_cors_config)
@jwt_required
def get_all_activities_route():
    return ActivityController.get_all_activities()

@activity_bp.route('/activities/<int:activity_id>', methods=['GET'])
@cross_origin(**activity_cors_config)
@jwt_required
def get_activity_route(activity_id):
    return ActivityController.get_activity(activity_id)

@activity_bp.route('/activities/<int:activity_id>', methods=['PUT'])
@cross_origin(**activity_cors_config)
@jwt_required
def update_activity_route(activity_id):
    return ActivityController.update_activity(activity_id)

@activity_bp.route('/activities/<int:activity_id>', methods=['DELETE'])
@cross_origin(**activity_cors_config)
@jwt_required
def delete_activity_route(activity_id):
    return ActivityController.delete_activity(activity_id)