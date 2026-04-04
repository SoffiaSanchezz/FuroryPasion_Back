from flask import Blueprint, request, make_response
from src.controllers.activity_controller import ActivityController
from src.middleware.jwt import jwt_required

activity_bp = Blueprint('activities', __name__)


def _cors_preflight():
    response = make_response('', 204)
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:4200')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, x-access-token, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response


@activity_bp.route('/activities', methods=['POST', 'OPTIONS'])
@jwt_required
def create_activity_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ActivityController.create_activity()

@activity_bp.route('/activities', methods=['GET', 'OPTIONS'])
@jwt_required
def get_all_activities_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ActivityController.get_all_activities()

@activity_bp.route('/activities/<int:activity_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_activity_route(activity_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ActivityController.get_activity(activity_id)

@activity_bp.route('/activities/<int:activity_id>', methods=['PUT', 'OPTIONS'])
@jwt_required
def update_activity_route(activity_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ActivityController.update_activity(activity_id)

@activity_bp.route('/activities/<int:activity_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required
def delete_activity_route(activity_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ActivityController.delete_activity(activity_id)
