<template>
  <div class="schedule-view">
    <div class="header">
      <h1>Schedule & Scores</h1>
      <input type="date" v-model="selectedDate" class="date-input">
    </div>
    
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p>Fetching schedule for {{ formattedDate }}...</p>
    </div>
    <div v-if="error" class="state-container error">
      <p>{{ error }}</p>
    </div>

    <div v-if="!loading && !error && schedule.length > 0" class="schedule-list">
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

    <div v-if="!loading && !error && schedule.length === 0" class="state-container">
      <p>No games scheduled for {{ formattedDate }}.</p>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';

function getTodayDateString() {
  const today = new Date();
  return today.toISOString().split('T')[0];
}

export default {
  name: 'HomeView',
  components: {}, 
  data() {
    return {
      schedule: [],
      loading: true,
      error: null, 
      selectedDate: null, 
    };
  },
  computed: {
    formattedDate() {
      if (!this.selectedDate) return '';
      const date = new Date(this.selectedDate);
      const utcDate = new Date(date.valueOf() + date.getTimezoneOffset() * 60000);
      return utcDate.toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric'
      });
    }
  },
  watch: {
    selectedDate(newDate, oldDate) {
      if (newDate && newDate !== oldDate) {
        this.$router.push({ query: { date: newDate } });
        this.fetchScheduleForDate(newDate);
      }
    }
  },
  created() {
    const dateFromUrl = this.$route.query.date;

    const initialDate = dateFromUrl || getTodayDateString();
    
    this.selectedDate = initialDate;
  },
  methods: {
    async fetchScheduleForDate(dateString) {
      this.loading = true;
      this.error = null; // 重置错误状态
      this.schedule = [];
      try {
        const response = await ApiService.getSchedule(dateString);
        this.schedule = response.data;
      } catch (error) {
        console.error(`Failed to fetch schedule for ${dateString}:`, error);
        this.error = 'Could not retrieve schedule. The API might be down or the request failed.';
      } finally {
        this.loading = false;
      }
    },
    formatGameType(type) {
      const gameTypes = {
        'R': 'Regular Season', 'F': 'Wild Card', 'D': 'Division Series',
        'L': 'Championship Series', 'W': 'World Series', 'S': 'Spring Training'
      };
      return gameTypes[type] || 'Other';
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
</style>