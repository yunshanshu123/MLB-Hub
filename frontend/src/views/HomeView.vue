<template>
  <div class="home-view">
    <div class="header">
      <h1>{{ view === 'schedule' ? 'Schedule & Scores' : 'League Standings' }}</h1>
      <div class="controls">
        <div class="view-toggle">
          <button :class="{ active: view === 'schedule' }" @click="view = 'schedule'">Schedule</button>
          <button :class="{ active: view === 'standings' }" @click="view = 'standings'">Standings</button>
        </div>
        <input v-if="view === 'schedule'" type="date" v-model="selectedDate" class="date-input">
      </div>
    </div>

    <div v-if="view === 'schedule'">
      <div v-if="scheduleLoading" class="state-container">
        <div class="spinner"></div>
        <p>Fetching schedule for {{ formattedDate }}...</p>
      </div>
      <div v-if="scheduleError" class="state-container error">
        <p>{{ scheduleError }}</p>
      </div>

      <div v-if="!scheduleLoading && !scheduleError && schedule.length > 0" class="schedule-list">
        <router-link v-for="game in schedule" :key="game.id" :to="'/game/' + game.id" class="game-link">
          <div class="game-card">
            <div class="card-header">
              <span class="game-type">{{ formatGameType(game.game_type) }}</span>
              <span class="status">{{ game.status }}</span>
            </div>
            <div class="card-body">
              <div class="team-column">
                <img :src="game.away_logo" :alt="game.away_team" class="team-logo">
                <span class="team-name">{{ game.away_team }}</span>
              </div>
              <div class="matchup-center">
                <span class="team-score">{{ game.away_score }}</span>
                <span class="vs">VS</span>
                <span class="team-score">{{ game.home_score }}</span>
              </div>
              <div class="team-column">
                <img :src="game.home_logo" :alt="game.home_team" class="team-logo">
                <span class="team-name">{{ game.home_team }}</span>
              </div>
            </div>
            <div class="card-footer">
              <span>{{ game.venue }}</span>
            </div>
          </div>
        </router-link>
      </div>

      <div v-if="!scheduleLoading && !scheduleError && schedule.length === 0" class="state-container">
        <p>No games scheduled for {{ formattedDate }}.</p>
      </div>
    </div>

    <div v-if="view === 'standings'">
      <div v-if="standingsLoading" class="state-container">
        <div class="spinner"></div>
        <p>Fetching latest standings...</p>
      </div>
      <div v-if="standingsError" class="state-container error">
        <p>{{ standingsError }}</p>
      </div>

      <div v-if="!standingsLoading && !standingsError && standings && standings.length > 0" class="standings-container">
        <div v-for="league in groupedStandings" :key="league.name" class="league-section">
          <h2>{{ league.name }}</h2>
          <div class="divisions-grid">
            <div v-for="division in league.divisions" :key="division.division" class="division-card">
              <h3>{{ division.division }}</h3>
              <table class="standings-table">
                <thead>
                  <tr>
                    <th class="team-col">Team</th>
                    <th>W</th>
                    <th>L</th>
                    <th>PCT</th>
                    <th>GB</th>
                    <th>STRK</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="team in division.teams" :key="team.id">
                    <td class="team-col">
                      <router-link :to="'/team/' + team.id" class="team-link">
                        <img :src="team.logo" :alt="team.name" class="team-logo-small">
                        <span>{{ team.name }}</span>
                      </router-link>
                    </td>
                    <td>{{ team.wins }}</td>
                    <td>{{ team.losses }}</td>
                    <td>{{ team.pct }}</td>
                    <td>{{ team.gb }}</td>
                    <td>{{ team.streak }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';

function getTodayDateString() {
  const today = new Date();
  const offset = today.getTimezoneOffset();
  const adjustedToday = new Date(today.getTime() - (offset * 60 * 1000));
  return adjustedToday.toISOString().split('T')[0];
}

export default {
  name: 'HomeView',
  data() {
    return {
      view: 'schedule',
      schedule: [],
      scheduleLoading: true,
      scheduleError: null, 
      selectedDate: null,
      standings: [],
      standingsLoading: false,
      standingsError: null,
    };
  },
  computed: {
    formattedDate() {
      if (!this.selectedDate) return '';
      const date = new Date(this.selectedDate);
      const utcDate = new Date(date.valueOf() + date.getTimezoneOffset() * 60000);
      return utcDate.toLocaleString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric'
      });
    },

    groupedStandings() {
      if (!Array.isArray(this.standings) || this.standings.length === 0) {
        return [];
      }

      const leaguesMap = this.standings.reduce((acc, divisionData) => {
        const leagueName = divisionData.league;

        if (!acc[leagueName]) {
          acc[leagueName] = {
            name: leagueName,
            divisions: [],
          };
        }

        acc[leagueName].divisions.push({
          division: divisionData.division,
          teams: divisionData.teams,
        });
        
        return acc;
      }, {});

      return Object.values(leaguesMap).sort((a, b) => a.name.localeCompare(b.name));
    }
  },
  watch: {
    selectedDate(newDate, oldDate) {
      if (newDate && newDate !== oldDate) {
        this.$router.push({ query: { date: newDate } }).catch(()=>{});
        this.fetchScheduleForDate(newDate);
      }
    },
    view(newView) {
      if (newView === 'standings' && this.standings.length === 0) {
        this.fetchStandings();
      }
    }
  },
  created() {
    const dateFromUrl = this.$route.query.date;
    const initialDate = dateFromUrl || getTodayDateString();

    this.fetchScheduleForDate(initialDate);
    
    this.selectedDate = initialDate;
  },
  methods: {
    async fetchScheduleForDate(dateString) {
      this.scheduleLoading = true;
      this.scheduleError = null;
      this.schedule = [];
      try {
        const response = await ApiService.getSchedule(dateString);
        this.schedule = response.data;
      } catch (error) {
        console.error(`Failed to fetch schedule for ${dateString}:`, error);
        this.scheduleError = 'Could not retrieve schedule. The API might be down or the request failed.';
      } finally {
        this.scheduleLoading = false;
      }
    },
    formatGameType(type) {
      const gameTypes = {
        'R': 'Regular Season', 'F': 'Wild Card', 'D': 'Division Series',
        'L': 'Championship Series', 'W': 'World Series', 'S': 'Spring Training'
      };
      return gameTypes[type] || 'Other';
    },
    async fetchStandings() {
      this.standingsLoading = true;
      this.standingsError = null;
      try {
        const response = await ApiService.getStandings();
        this.standings = response.data; 
      } catch (error) {
        console.error("Failed to fetch standings:", error);
        this.standingsError = 'Could not retrieve standings data.';
      } finally {
        this.standingsLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.game-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.date-input { font-family: inherit; font-size: 1rem; padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; width: 180px; }

.state-container { 
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #888; 
  padding: 40px 0; 
  font-size: 1.1em; 
}
.state-container.error p {
  color: #d9534f;
}
.state-container p {
  margin: 15px 0 0;
}
.spinner { 
  width: 32px; height: 32px; border: 4px solid #ccc; 
  border-top-color: #002D72; border-radius: 50%; 
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.schedule-list { display: flex; flex-direction: column; gap: 15px; }
.game-card { border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s ease-in-out; }
.game-card:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.1); transform: scale(1.02); }
.card-header { display: flex; justify-content: space-between; background-color: #f7f7f7; padding: 8px 15px; font-size: 0.85em; color: #555; border-bottom: 1px solid #e0e0e0; }
.status { font-weight: bold; color: #d9534f; }
.card-body { display: flex; justify-content: space-between; align-items: center; padding: 25px 15px; }
.team-column { display: flex; flex-direction: column; align-items: center; text-align: center; width: 35%; }
.team-logo { width: 60px; height: 60px; margin-bottom: 10px; }
.team-name { font-size: 1.1em; font-weight: 600; color: #333; }
.matchup-center { display: flex; align-items: center; justify-content: center; gap: 20px; width: 20%; }
.vs { font-size: 1em; font-weight: 600; color: #999; }
.team-score { font-size: 2.2em; font-weight: bold; color: #000; }
.card-footer { background-color: #f7f7f7; text-align: center; padding: 8px 15px; font-size: 0.8em; color: #777; border-top: 1px solid #e0e0e0; }

.controls {
  display: flex;
  align-items: center;
  gap: 15px;
}
.view-toggle {
  display: flex;
  background-color: #e9ecef;
  border-radius: 8px;
  padding: 4px;
}
.view-toggle button {
  padding: 6px 18px;
  font-size: 1em;
  border: none;
  background-color: transparent;
  color: #555;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}
.view-toggle button.active {
  background-color: #fff;
  color: #002D72;
  font-weight: bold;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.standings-container {
  display: flex;
  flex-direction: column;
  gap: 40px;
}
.league-section h2 {
  font-size: 1.8em;
  margin-bottom: 20px;
  text-align: center;
  border-bottom: 2px solid #002D72;
  padding-bottom: 10px;
}
.divisions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}
.division-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.division-card h3 {
  margin: 0 0 15px;
  text-align: center;
}
.standings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95em;
}
.standings-table th, .standings-table td {
  text-align: right;
  padding: 10px 5px;
  border-bottom: 1px solid #f0f2f5;
}
.standings-table th {
  color: #6c757d;
  font-weight: normal;
}
.standings-table .team-col {
  text-align: left;
  width: 60%;
}
.team-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #333;
  font-weight: 500;
}
.team-link:hover {
  color: #002D72;
}
.team-logo-small {
  width: 24px;
  height: 24px;
}
</style>