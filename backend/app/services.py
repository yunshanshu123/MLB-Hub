import requests
from datetime import datetime

# MLB 官方 API 的基础地址
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

def get_schedule_and_scores(date_str=None):
    """
    (此函数保持不变)
    从 MLB Data API 获取指定日期的赛程和实时比分。
    """
    if not date_str:
        date_str = datetime.today().strftime('%Y-%m-%d')
    
    url = f"{MLB_API_BASE}/schedule?sportId=1&date={date_str}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        games_processed = []
        if data.get("dates"):
            raw_games = data["dates"][0]["games"]
            for game in raw_games:
                away_team_id = game["teams"]["away"]["team"]["id"]
                home_team_id = game["teams"]["home"]["team"]["id"]

                processed_game = {
                    "id": game["gamePk"],
                    "status": game["status"]["detailedState"],
                    "home_team": game["teams"]["home"]["team"]["name"],
                    "away_team": game["teams"]["away"]["team"]["name"],
                    "home_score": game["teams"]["home"].get("score", 0),
                    "away_score": game["teams"]["away"].get("score", 0),
                    "venue": game["venue"]["name"],
                    "time": game.get("gameDate"),
                    "game_type": game["gameType"],
                    "away_logo": f"https://www.mlbstatic.com/team-logos/{away_team_id}.svg",
                    "home_logo": f"https://www.mlbstatic.com/team-logos/{home_team_id}.svg"
                }
                games_processed.append(processed_game)
        
        return games_processed

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from MLB API: {e}")
        return []

def search_mlb_data(query):
    """
    (此函数已修正)
    使用官方 MLB Stats API 搜索球员和球队，并融合成一个列表。
    """
    processed_results = []
    
    try:
        # --- 1. 搜索球员 ---
        player_search_url = f"{MLB_API_BASE}/people/search?names={query}"
        player_response = requests.get(player_search_url)
        player_response.raise_for_status()
        players_data = player_response.json().get('people', [])

        for basic_player_info in players_data:
            player_id = basic_player_info.get('id')
            if not player_id:
                continue

            detailed_player_url = f"{MLB_API_BASE}/people/{player_id}?hydrate=currentTeam,primaryPosition"
            detailed_response = requests.get(detailed_player_url)
            detailed_response.raise_for_status()
            
            player_list = detailed_response.json().get('people', [])
            if not player_list:
                continue
            player = player_list[0]

            team_info = player.get('currentTeam', {})
            position_info = player.get('primaryPosition', {})
            
            processed_results.append({
                'id': f"player-{player['id']}",
                'type': 'player',
                'name': player.get('fullName', 'N/A'),
                'photo': f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player['id']}/headshot/67/current",
                'age': player.get('currentAge'),
                'team': team_info.get('name'),
                'position': position_info.get('abbreviation')
            })

        # --- 2. 搜索球队 ---
        all_teams_url = f"{MLB_API_BASE}/teams?sportId=1"
        team_response = requests.get(all_teams_url)
        team_response.raise_for_status()
        teams_data = team_response.json().get('teams', [])
        
        query_lower = query.lower()
        
        for team in teams_data:
            if query_lower in team.get('name', '').lower() or \
               query_lower in team.get('teamName', '').lower(): # <-- 此处已从 query_e 修正为 query_lower
                
                processed_results.append({
                    'id': f"team-{team['id']}",
                    'type': 'team',
                    'name': team.get('name'),
                    'logo': f"https://www.mlbstatic.com/team-logos/{team['id']}.svg",
                    'venue': team.get('venue', {}).get('name'),
                    'league': team.get('league', {}).get('name'),
                    'division': team.get('division', {}).get('name'),
                })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching search data from MLB API: {e}")
        return {"error": f"Failed to fetch data from external provider. Details: {e}"}

    return processed_results