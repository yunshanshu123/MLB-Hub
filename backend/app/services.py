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

MLB_TEAM_KEYWORDS = [
    'd-backs', 'diamondbacks', 'braves', 'orioles', 'red sox', 'cubs', 'white sox', 
    'reds', 'guardians', 'rockies', 'tigers', 'astros', 'royals', 'angels', 
    'dodgers', 'marlins', 'brewers', 'twins', 'mets', 'yankees', 'athletics', 
    'a\'s', 'phillies', 'pirates', 'padres', 'giants', 'mariners', 'cardinals', 
    'rays', 'rangers', 'blue jays', 'nationals'
]
MLB_SUPERSTAR_KEYWORDS = [
    'ohtani', 'judge', 'trout', 'soto', 'betts', 'acuna',  'raleigh', 'springer', 
    'freeman', 'harper', 'kershaw', 'degrom', 'scherzer', 'verlander', 'cole', 'schwarber', 
    'skenes', 'skubal', 'duran', 'snell', 'yamamoto'
]
MLB_JARGON_KEYWORDS = [
    'pitcher', 'catcher', 'infielder', 'outfielder', 'hitter', 'batter', 'bullpen',
    'strikeout', 'home run', 'grand slam', 'no-hitter', 'perfect game', 'inning',
    'dugout', 'umpire', 'world series', 'cy young', 'double play'
]
MLB_GENERAL_KEYWORDS = [
    'playoffs', 'all-star', 'mvp', 'championship', 'division series'
]
COMPETITOR_LEAGUE_KEYWORDS = [
    'nfl', 'nba', 'nhl', 'pga', 'nascar', 'mls', 'premier league', 'f1', 'formula 1'
]

def get_mlb_news(page=1, per_page=20):
    if not Config.NEWSAPI_KEY:
        print("Warning: NewsAPI Key not configured.")
        return {"error": "News service is not configured on the server."}

    news_api_url = "https://newsapi.org/v2/everything"
    sources = "espn,fox-sports,cbs-sports,bleacher-report,nbc-sports"
    params = {
        'q': '"MLB" OR "baseball"', 'apiKey': Config.NEWSAPI_KEY,
        'sources': sources, 'sortBy': 'publishedAt',
        'pageSize': 100, 'language': 'en'
    }

    try:
        response = requests.get(news_api_url, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        
        scored_articles = []
        for article in articles:
            if not article.get('content') or article.get('title') == '[Removed]':
                continue

            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content_to_check = title + " " + description

            score = 0
            if any(keyword in content_to_check for keyword in MLB_TEAM_KEYWORDS): score += 4
            if 'mlb' in content_to_check or 'major league baseball' in content_to_check: score += 3
            if any(keyword in content_to_check for keyword in MLB_SUPERSTAR_KEYWORDS): score += 3
            if any(keyword in content_to_check for keyword in MLB_JARGON_KEYWORDS): score += 2
            if any(keyword in content_to_check for keyword in MLB_GENERAL_KEYWORDS): score += 1
            if any(keyword in title for keyword in COMPETITOR_LEAGUE_KEYWORDS): score -= 3

            if score >= 1:
                processed_article = {
                    'id': article.get('url'), 'title': article.get('title'),
                    'url': article.get('url'), 'date': article.get('publishedAt'),
                    'summary': article.get('description'), 'thumbnail': article.get('urlToImage')
                }
                scored_articles.append({'article': processed_article, 'score': score})

        scored_articles.sort(key=lambda x: x['score'], reverse=True)
        top_40_articles = [item['article'] for item in scored_articles[:40]]

        top_40_articles.sort(key=lambda x: x['date'], reverse=True)

        total_results = len(top_40_articles)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_articles = top_40_articles[start_index:end_index]
        has_more = end_index < total_results

        return {
            "articles": paginated_articles, "page": page,
            "totalResults": total_results, "hasMore": has_more
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from NewsAPI: {e}")
        return {"error": "Failed to fetch news from the provider."}

def get_youtube_highlights(query=None):
    if not Config.YOUTUBE_API_KEY:
        print("Warning: YouTube API Key not configured.")
        return {"error": "Video service is not configured on the server."}

    youtube_api_url = "https://www.googleapis.com/youtube/v3/search"
    
    search_term = ""
    if query:
        search_term = f"MLB {query}"
    else:
        search_term = "MLB Highlights"

    params = {
        'key': Config.YOUTUBE_API_KEY,
        'part': 'snippet',
        'q': search_term,
        'type': 'video',
        'maxResults': 12,
        'order': 'relevance'
    }

    try:
        response = requests.get(youtube_api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        processed_videos = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId')
            if video_id:
                processed_videos.append({
                    'videoId': video_id,
                    'title': snippet.get('title'),
                    'thumbnailUrl': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                    'publishedAt': snippet.get('publishedAt')
                })
            
        return processed_videos

    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos from YouTube API: {e.response.text if e.response else e}")
        return {"error": "Failed to fetch videos from the provider."}
    
def get_league_standings(season=None):
    if not season:
        season = datetime.now().year
        
    url = f"{MLB_API_BASE}/standings?leagueId=103,104&season={season}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        processed_standings = []
        for record in data.get('records', []):
            division_name = record.get('division', {}).get('name')
            league_name = record.get('league', {}).get('name')
            
            teams_in_division = []
            for team_entry in record.get('teamRecords', []):
                team_info = team_entry.get('team', {})
                league_record = team_entry.get('leagueRecord', {})
                teams_in_division.append({
                    'id': team_info.get('id'),
                    'name': team_info.get('name'),
                    'logo': f"https://www.mlbstatic.com/team-logos/{team_info.get('id')}.svg",
                    'wins': league_record.get('wins', 0),
                    'losses': league_record.get('losses', 0),
                    'pct': league_record.get('pct', '.000'),
                    'gb': team_entry.get('gamesBack', '--'),
                    'streak': team_entry.get('streak', {}).get('streakCode', '-')
                })
            
            processed_standings.append({
                'league': league_name,
                'division': division_name,
                'teams': teams_in_division
            })
            
        return processed_standings

    except requests.exceptions.RequestException as e:
        print(f"Error fetching standings from MLB API: {e}")
        return {"error": "Failed to fetch league standings from the provider."}

