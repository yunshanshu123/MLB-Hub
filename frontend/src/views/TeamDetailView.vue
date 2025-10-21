<template>
  <div class="team-detail-view">
    <div class="view-header">
      <a @click="goBack" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M400-80 0-480l400-400 71 71-329 329 329 329-71 71Z"/></svg>
        <span>Back</span>
      </a>
    </div>

    <LoadingIndicator v-if="loading" message="Loading Team Data..." />
    <ErrorDisplay 
      v-if="error" 
      title="Could not load team data." 
      :message="error" 
      @goBack="goBack" 
    />

    <transition name="fade-in">
      <div v-if="!loading && !error && team" class="team-content">
        <div class="team-header white-card">
          <img :src="team.logo" :alt="team.name" class="team-logo-large">
          <div class="team-info">
            <h1>{{ team.name }}</h1>
            <div class="team-bio">
              <span>{{ team.city }}, {{ team.venue }}</span>
              <span> • </span>
              <span>Est: {{ team.firstYear }}</span>
              <span> • </span>
              <span>{{ team.league }} {{ team.division }}</span>
            </div>
          </div>
          <div v-if="team.weather" class="weather-widget">
            <i class="weather-icon" :class="weatherIconClass"></i>
            <div class="weather-info">
              <span class="weather-temp">{{ team.weather.temperature }}°C</span>
              <span class="weather-desc">{{ team.weather.description }}</span>
            </div>
          </div>
        </div>

        <div class="roster-section white-card">
          <h2>Team Roster</h2>
          <div class="roster-grid">
            <router-link v-for="player in team.roster" :key="player.id" :to="'/player/' + player.id" class="player-card-link">
              <div class="player-card">
                <img :src="getPlayerPhotoUrl(player.id)" @error="imageError" class="player-photo-small">
                <div class="player-card-info">
                  <span class="player-card-name">#{{ player.jerseyNumber }} {{ player.name }}</span>
                  <span class="player-card-pos">{{ player.position }}</span>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import ErrorDisplay from '@/components/ErrorDisplay.vue';

const OWM_ICON_MAP = {
  '01d': 'wi-day-sunny', '01n': 'wi-night-clear',
  '02d': 'wi-day-cloudy', '02n': 'wi-night-alt-cloudy',
  '03d': 'wi-cloud', '03n': 'wi-cloud',
  '04d': 'wi-cloudy', '04n': 'wi-cloudy',
  '09d': 'wi-showers', '09n': 'wi-showers',
  '10d': 'wi-day-rain', '10n': 'wi-night-alt-rain',
  '11d': 'wi-thunderstorm', '11n': 'wi-thunderstorm',
  '13d': 'wi-snow', '13n': 'wi-snow',
  '50d': 'wi-fog', '50n': 'wi-fog',
};

export default {
  name: 'TeamDetailView',
  components: {
    LoadingIndicator,
    ErrorDisplay
  },
  data() {
    return {
      teamId: null,
      team: null,
      loading: true,
      error: null,
    };
  },
  computed: {
    weatherIconClass() {
      if (this.team && this.team.weather && this.team.weather.icon) {
        const iconCode = this.team.weather.icon;
        return ['wi', OWM_ICON_MAP[iconCode] || 'wi-na'];
      }
      return 'wi-na';
    }
  },
  async created() {
    this.teamId = this.$route.params.id;
    await this.fetchTeamData();
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    async fetchTeamData() {
      this.loading = true;
      this.error = null;
      try {
        const response = await ApiService.getTeamDetails(this.teamId);
        this.team = response.data;
      } catch (err) {
        console.error("Failed to fetch team data:", err);
        this.error = err.response?.data?.error || "An unknown error occurred.";
      } finally {
        this.loading = false;
      }
    },
    getPlayerPhotoUrl(playerId) {
      return `https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/${playerId}/headshot/67/current`;
    },
    imageError(event) {
      event.target.src = 'https://www.mlbstatic.com/team-logos/league/1.svg';
    }
  }
};
</script>

<style scoped>
.fade-in-enter-active, .fade-in-leave-active { transition: opacity 0.5s ease; }
.fade-in-enter-from, .fade-in-leave-to { opacity: 0; }

.team-detail-view { background-color: #f0f2f5; padding: 20px 40px; min-height: 100vh; }
.white-card { background: #fff; border-radius: 12px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 30px; }

.view-header {
  margin-bottom: 20px;
}
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: #fff;
  color: #333;
  padding: 10px 18px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
  cursor: pointer;
}
.back-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}
.back-link svg {
  fill: #333;
}

.team-header { display: flex; align-items: center; gap: 25px; position: relative; }
.team-logo-large { width: 120px; height: 120px; object-fit: contain; }
.team-info h1 { margin: 0 0 5px; font-size: 2.5em; color: #212529; }
.team-bio { display: flex; gap: 8px; color: #6c757d; font-weight: 500; }

.weather-widget { display: flex; align-items: center; gap: 10px; margin-left: auto; background: #f8f9fa; padding: 10px 15px; border-radius: 8px; }

.weather-icon {
  font-size: 2.5em;
  color: #002D72;
  line-height: 1;
}

.weather-info { display: flex; flex-direction: column; text-align: left; }
.weather-temp { font-size: 1.5em; font-weight: bold; color: #212529; }
.weather-desc { font-size: 0.9em; color: #6c757d; text-transform: capitalize; }

.roster-section h2 { font-size: 1.8em; margin-bottom: 20px; text-align: center; }
.roster-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
.player-card-link { text-decoration: none; color: inherit; }
.player-card { display: flex; align-items: center; gap: 15px; background: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e9ecef; transition: all 0.2s ease; }
.player-card:hover { transform: scale(1.02); box-shadow: 0 4px 8px rgba(0,0,0,0.08); border-color: #002D72; }
.player-photo-small { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; background: #fff; }
.player-card-info { display: flex; flex-direction: column; }
.player-card-name { font-weight: bold; font-size: 1.1em; }
.player-card-pos { font-size: 0.9em; color: #6c757d; }
</style>