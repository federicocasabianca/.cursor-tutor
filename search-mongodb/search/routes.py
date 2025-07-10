from flask import Blueprint, request, jsonify
from search.service import search_materials, get_material_by_id, store_search_query

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def search():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 14))
    result = search_materials(query, page, limit)
    return jsonify(result)

@search_bp.route('/search/material/<int:material_id>')
def search_material_by_id_route(material_id):
    result = get_material_by_id(material_id)
    if result is None:
        return jsonify({"error": "Material not found"}), 404
    return jsonify(result)
