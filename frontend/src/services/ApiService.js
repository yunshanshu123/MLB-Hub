import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
  getSchedule(dateString) {
    const url = dateString ? `/schedule/${dateString}` : '/schedule';
    return apiClient.get(url);
  },
  searchData(query) {
    return apiClient.get('/search', { params: { q: query } });
  },
  getPlayerStats(playerId) {
    return apiClient.get(`/player/${playerId}/stats`);
  },
  getPlayerDetails(playerId) {
    return apiClient.get(`/player/${playerId}/details`);
  },
  getLeagueLeaders() {
    return apiClient.get('/leaders');
  },
  getTeamDetails(teamId) {
    return apiClient.get(`/team/${teamId}/details`);
  }
};