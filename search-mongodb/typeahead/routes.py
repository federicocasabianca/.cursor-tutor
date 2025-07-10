from flask import Blueprint, request, jsonify
from typeahead.service import get_typeahead_suggestions

typeahead_bp = Blueprint('typeahead', __name__)

@typeahead_bp.route('/typeahead')
def typeahead():
    query = request.args.get('q', '').strip()
    return jsonify(get_typeahead_suggestions(query))
