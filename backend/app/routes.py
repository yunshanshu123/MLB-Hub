from flask import Blueprint, jsonify, request
# 导入我们新的 service 函数 search_mlb_data
from .services import get_schedule_and_scores, search_mlb_data
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

# (此路由保持不变)
@api_bp.route('/schedule', methods=['GET'])
@api_bp.route('/schedule/<date_str>', methods=['GET'])
def schedule(date_str=None):
    if date_str is None:
        date_str = datetime.today().strftime('%Y-%m-%d')
    data = get_schedule_and_scores(date_str)
    return jsonify(data)

@api_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')

    if not query:
        return jsonify({"error": "A search query 'q' is required."}), 400

    # --- 关键修改：调用新的、可靠的搜索函数 ---
    results = search_mlb_data(query)
    
    if 'error' in results:
        return jsonify(results), 500

    return jsonify(results)