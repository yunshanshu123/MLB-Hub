from flask import Blueprint, jsonify, request
from .services import (get_schedule_and_scores, search_mlb_data, get_player_stats, 
                       get_player_details, get_league_leaders, get_team_details,
                       get_game_details, get_mlb_news, get_youtube_highlights)
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

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
    results = search_mlb_data(query)
    if 'error' in results:
        return jsonify(results), 500
    return jsonify(results)

@api_bp.route('/player/<int:player_id>/stats', methods=['GET'])
def player_stats(player_id):
    stats = get_player_stats(player_id)
    if 'error' in stats:
        if "No statistical data" in stats['error']:
            return jsonify(stats), 404
        return jsonify(stats), 500
    return jsonify(stats)

@api_bp.route('/player/<int:player_id>/details', methods=['GET'])
def player_details(player_id):
    details = get_player_details(player_id)
    if 'error' in details:
        return jsonify(details), 404
    return jsonify(details)

@api_bp.route('/leaders', methods=['GET'])
def league_leaders():
    leaders = get_league_leaders()
    if 'error' in leaders:
        return jsonify(leaders), 500
    return jsonify(leaders)

@api_bp.route('/team/<int:team_id>/details', methods=['GET'])
def team_details(team_id):
    details = get_team_details(team_id)
    if 'error' in details:
        return jsonify(details), 404
    return jsonify(details)

@api_bp.route('/game/<int:game_id>/details', methods=['GET'])
def game_details(game_id):
    details = get_game_details(game_id)
    if 'error' in details:
        return jsonify(details), 500
    return jsonify(details)

@api_bp.route('/news', methods=['GET'])
def get_news():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1   
    news_data = get_mlb_news(page=page)
    if 'error' in news_data:
        return jsonify(news_data), 503
    return jsonify(news_data)

@api_bp.route('/highlights', methods=['GET'])
def get_highlights():
    query = request.args.get('q', None) 
    videos = get_youtube_highlights(query=query)
    if 'error' in videos:
        return jsonify(videos), 503
    return jsonify(videos)