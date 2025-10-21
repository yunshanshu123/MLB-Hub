import requests
from datetime import datetime
from config import Config

MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

def get_schedule_and_scores(date_str=None):
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
                    "id": game["gamePk"], "status": game["status"]["detailedState"],
                    "home_team": game["teams"]["home"]["team"]["name"],
                    "away_team": game["teams"]["away"]["team"]["name"],
                    "home_score": game["teams"]["home"].get("score", 0),
                    "away_score": game["teams"]["away"].get("score", 0),
                    "venue": game["venue"]["name"], "time": game.get("gameDate"),
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
    processed_results = []
    try:
        player_search_url = f"{MLB_API_BASE}/people/search?names={query}"
        player_response = requests.get(player_search_url)
        player_response.raise_for_status()
        
        players_data = player_response.json().get('people', [])
        player_ids = [str(player.get('id')) for player in players_data if player.get('id')]

        if player_ids:
            ids_string = ",".join(player_ids)
            hydrate_params = "currentTeam,primaryPosition"
            detailed_players_url = f"{MLB_API_BASE}/people?personIds={ids_string}&hydrate={hydrate_params}"
            
            detailed_response = requests.get(detailed_players_url)
            detailed_response.raise_for_status()
            
            detailed_players_list = detailed_response.json().get('people', [])
            
            for player in detailed_players_list:
                team_info = player.get('currentTeam', {})
                position_info = player.get('primaryPosition', {})
                processed_results.append({
                    'id': f"player-{player['id']}", 'type': 'player',
                    'name': player.get('fullName', 'N/A'),
                    'photo': f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player['id']}/headshot/67/current",
                    'age': player.get('currentAge'),
                    'team': team_info.get('name'),
                    'position': position_info.get('abbreviation')
                })

        all_teams_url = f"{MLB_API_BASE}/teams?sportId=1"
        team_response = requests.get(all_teams_url)
        team_response.raise_for_status()
        teams_data = team_response.json().get('teams', [])
        query_lower = query.lower()
        for team in teams_data:
            if query_lower in team.get('name', '').lower() or \
               query_lower in team.get('teamName', '').lower():
                processed_results.append({
                    'id': f"team-{team['id']}", 'type': 'team',
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

def get_player_stats(player_id):
    try:
        stats_url = f"{MLB_API_BASE}/people/{player_id}/stats?stats=yearByYear&group=hitting,pitching"
        response = requests.get(stats_url)
        response.raise_for_status()
        raw_stats = response.json().get('stats', [])
        season_stats = {}
        for stat_group in raw_stats:
            group_name = stat_group.get('group', {}).get('displayName', '').lower()
            splits = stat_group.get('splits', [])
            last_split_by_season = {}
            for split in splits:
                season = split.get('season')
                if season:
                    last_split_by_season[season] = split
            for season, split in last_split_by_season.items():
                if season not in season_stats:
                    season_stats[season] = {}
                stat_data = split.get('stat', {})
                stat_data['team_name'] = split.get('team', {}).get('name', 'N/A')
                season_stats[season][group_name] = stat_data
        if not season_stats:
             return {"error": "No statistical data found for this player."}
        return season_stats
    except requests.exceptions.RequestException as e:
        print(f"Error fetching player stats from MLB API: {e}")
        return {"error": "Failed to fetch player stats from the provider."}

def get_player_details(player_id):
    try:
        detailed_player_url = f"{MLB_API_BASE}/people/{player_id}?hydrate=currentTeam,primaryPosition"
        response = requests.get(detailed_player_url)
        response.raise_for_status()
        player_list = response.json().get('people', [])
        if not player_list:
            return {"error": "Player not found."}
        player = player_list[0]
        team_info = player.get('currentTeam', {})
        position_info = player.get('primaryPosition', {})
        player_details = {
            'id': f"player-{player['id']}", 'type': 'player',
            'name': player.get('fullName', 'N/A'),
            'photo': f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player['id']}/headshot/67/current",
            'age': player.get('currentAge'),
            'team': team_info.get('name'),
            'position': position_info.get('abbreviation'),
            'jerseyNumber': player.get('primaryNumber', '-'),
            'birthDate': player.get('birthDate', 'N/A')
        }
        return player_details
    except requests.exceptions.RequestException as e:
        print(f"Error fetching player details from MLB API: {e}")
        return {"error": "Failed to fetch player details from the provider."}

def get_league_leaders():
    try:
        current_season = datetime.now().year
        hitting_categories = "homeRuns,battingAverage,runsBattedIn,onBasePlusSlugging,hits,runs"
        pitching_categories = "earnedRunAverage,wins,strikeouts,walksAndHitsPerInningPitched,saves,inningsPitched"
        leaders_data = { "hitting": {}, "pitching": {} }
        hitting_url = (f"{MLB_API_BASE}/stats/leaders?leaderCategories={hitting_categories}"
                       f"&sportId=1&season={current_season}&gameType=R&limit=5&statGroup=hitting")
        hitting_response = requests.get(hitting_url)
        hitting_response.raise_for_status()
        for category in hitting_response.json().get('leagueLeaders', []):
            stat_name = category.get('leaderCategory')
            leaders_data["hitting"][stat_name] = [
                {
                    "rank": leader.get('rank'), "value": leader.get('value'),
                    "id": leader.get('person', {}).get('id'),
                    "name": leader.get('person', {}).get('fullName')
                } for leader in category.get('leaders', [])
            ]
        pitching_url = (f"{MLB_API_BASE}/stats/leaders?leaderCategories={pitching_categories}"
                        f"&sportId=1&season={current_season}&gameType=R&limit=5&statGroup=pitching")
        pitching_response = requests.get(pitching_url)
        pitching_response.raise_for_status()
        for category in pitching_response.json().get('leagueLeaders', []):
            stat_name = category.get('leaderCategory')
            leaders_data["pitching"][stat_name] = [
                {
                    "rank": leader.get('rank'), "value": leader.get('value'),
                    "id": leader.get('person', {}).get('id'),
                    "name": leader.get('person', {}).get('fullName')
                } for leader in category.get('leaders', [])
            ]
        return leaders_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching league leaders from MLB API: {e}")
        return {"error": "Failed to fetch league leaders from the provider."}

def get_team_details(team_id):
    try:
        team_info_url = f"{MLB_API_BASE}/teams/{team_id}"
        team_info_response = requests.get(team_info_url)
        team_info_response.raise_for_status()
        
        teams = team_info_response.json().get('teams', [])
        if not teams:
            return {"error": "Team not found."}
        team_data = teams[0]
        city = team_data.get('locationName')
        team_name_for_map = team_data.get('teamName')
        roster_url = f"{MLB_API_BASE}/teams/{team_id}/roster"
        roster_response = requests.get(roster_url)
        roster_response.raise_for_status()
        
        roster_list = []
        for player_entry in roster_response.json().get('roster', []):
            person = player_entry.get('person', {})
            position = player_entry.get('position', {})
            roster_list.append({
                "id": person.get('id'),
                "name": person.get('fullName'),
                "jerseyNumber": player_entry.get('jerseyNumber', '-'),
                "position": position.get('abbreviation')
            })
        
        team_details = {
            'id': team_data.get('id'),
            'name': team_data.get('name'),
            'logo': f"https://www.mlbstatic.com/team-logos/{team_id}.svg",
            'venue': team_data.get('venue', {}).get('name'),
            'city': city,
            'firstYear': team_data.get('firstYearOfPlay'),
            'league': team_data.get('league', {}).get('name'),
            'division': team_data.get('division', {}).get('name'),
            'roster': roster_list,
            'weather': get_weather_for_city(team_name_for_map if team_name_for_map in ["NY Mets", "NY Yankees", "Chi Cubs", "Chi White Sox"] else city)
        }
        return team_details

    except requests.exceptions.RequestException as e:
        print(f"Error fetching team details from MLB API: {e}")
        return {"error": "Failed to fetch team details from the provider."}

def get_weather_for_city(city_name):
    if not Config.OPENWEATHER_API_KEY:
        print("Warning: OpenWeather API Key not configured.")
        return None
    city_map = {
        "NY Mets": "New York", "NY Yankees": "New York",
        "Chi Cubs": "Chicago", "Chi White Sox": "Chicago",
    }
    search_city = city_map.get(city_name, city_name)
    weather_url = ("https://api.openweathermap.org/data/2.5/weather"
                   f"?q={search_city}&appid={Config.OPENWEATHER_API_KEY}&units=metric")
    try:
        response = requests.get(weather_url)
        if response.status_code == 401:
            print("Error: OpenWeather API Key is invalid or not yet active.")
            return {"error": "Invalid Weather API Key"}
        response.raise_for_status()
        data = response.json()
        weather_info = data.get('weather', [{}])[0]
        main_info = data.get('main', {})
        return {
            "temperature": round(main_info.get('temp')),
            "description": weather_info.get('main'),
            "icon": weather_info.get('icon')
        }
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch weather for city '{search_city}': {e}")
        return {"error": "Weather service unavailable"}

def get_game_details(game_id):
    try:
        game_url_live = f"{MLB_API_BASE}/game/{game_id}/feed/live"
        response = requests.get(game_url_live)

        if response.status_code == 404:
            game_url_context = f"{MLB_API_BASE}/game/{game_id}/contextMetrics"
            linescore_url = f"{MLB_API_BASE}/game/{game_id}/linescore"
            boxscore_url = f"{MLB_API_BASE}/game/{game_id}/boxscore"
            
            game_resp = requests.get(game_url_context)
            game_resp.raise_for_status()
            game_data = game_resp.json().get('game', {})
            
            linescore_resp = requests.get(linescore_url)
            linescore_resp.raise_for_status()
            linescore = linescore_resp.json()
            
            boxscore_resp = requests.get(boxscore_url)
            boxscore_resp.raise_for_status()
            boxscore = boxscore_resp.json().get('teams', {})
        
        else:
            response.raise_for_status()
            data = response.json()
            live_data = data.get('liveData', {})
            game_data = data.get('gameData', {})
            linescore = live_data.get('linescore', {})
            boxscore = live_data.get('boxscore', {}).get('teams', {})

        players_data = { "away": [], "home": [] }
        for team in ["away", "home"]:
            team_players = boxscore.get(team, {}).get('players', {})
            for player_id_key, player_stats in team_players.items():
                players_data[team].append({
                    "id": player_stats.get('person', {}).get('id'),
                    "name": player_stats.get('person', {}).get('fullName'),
                    "jerseyNumber": player_stats.get('jerseyNumber', '-'),
                    "position": player_stats.get('position', {}).get('abbreviation'),
                    "stats": {
                        "batting": player_stats.get('stats', {}).get('batting', {}),
                        "pitching": player_stats.get('stats', {}).get('pitching', {})
                    }
                })
        
        away_team_box_info = boxscore.get('away', {}).get('team', {})
        home_team_box_info = boxscore.get('home', {}).get('team', {})

        return {
            "status": game_data.get('status', {}).get('detailedState', 'Final'),
            "venue": game_data.get('venue', {}).get('name'),
            "away_team": away_team_box_info.get('name'),
            "home_team": home_team_box_info.get('name'),
            "away_logo": f"https://www.mlbstatic.com/team-logos/{away_team_box_info.get('id')}.svg",
            "home_logo": f"https://www.mlbstatic.com/team-logos/{home_team_box_info.get('id')}.svg",
            "linescore": linescore,
            "players": players_data,
            "away_team_id": away_team_box_info.get('id'),
            "home_team_id": home_team_box_info.get('id')
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching game details from MLB API: {e}")
        return {"error": "Failed to fetch game details from the provider."}