from flask import Blueprint
from src.controllers.search_controller import SearchController
from src.middleware.jwt import jwt_required

search_bp = Blueprint('search', __name__)


@search_bp.route('/search', methods=['GET'])
@jwt_required
def search_route():
    return SearchController.search()
