import requests
from datetime import datetime

# MLB 官方 API 的基础地址
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

def get_schedule_and_scores(date_str=None):
    """
    从 MLB Data API 获取指定日期的赛程和实时比分。
    现在返回的数据中包含了比赛类型和球队Logo。
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
                # 新增：获取主客队的ID
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
                    # 新增：比赛类型 (例如 "R" 代表常规赛)
                    "game_type": game["gameType"],
                    # 新增：根据球队ID构造官方SVG Logo的URL
                    "away_logo": f"https://www.mlbstatic.com/team-logos/{away_team_id}.svg",
                    "home_logo": f"https://www.mlbstatic.com/team-logos/{home_team_id}.svg"
                }
                games_processed.append(processed_game)
        
        return games_processed

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from MLB API: {e}")
        return []