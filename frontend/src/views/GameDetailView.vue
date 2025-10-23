<template>
  <div class="game-detail-view">
    <div class="view-header">
      <a @click="goBack" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M400-80 0-480l400-400 71 71-329 329 329 329-71 71Z"/></svg>
        <span>Back to Schedule</span>
      </a>
    </div>

    <LoadingIndicator v-if="loading" message="Loading Game Details..." />
    
    <ErrorDisplay 
      v-if="error" 
      title="Game Data Unavailable" 
      message="Detailed statistics may not be available for games that have not yet started or were canceled." 
      @goBack="goBack" 
    />

    <transition name="fade-in">
      <div v-if="!loading && !error && game" class="game-content">
        <div class="game-header white-card">
          <div class="header-info">
            <span>{{ game.venue }}</span>
            <span class="status">{{ game.status }}</span>
          </div>
          <div class="scoreboard">
            <div class="team away">
              <router-link :to="'/team/' + game.away_team_id" class="team-info-link">
                <div class="team-info">
                  <img :src="game.away_logo" class="team-logo">
                  <span class="team-name">{{ game.away_team }}</span>
                </div>
              </router-link>
              <span class="team-score">{{ game.linescore.teams.away.runs || 0 }}</span>
            </div>
            <div class="vs">FINAL</div>
            <div class="team home">
              <span class="team-score">{{ game.linescore.teams.home.runs || 0 }}</span>
              <router-link :to="'/team/' + game.home_team_id" class="team-info-link">
                <div class="team-info">
                  <img :src="game.home_logo" class="team-logo">
                  <span class="team-name">{{ game.home_team }}</span>
                </div>
              </router-link>
            </div>
          </div>
        </div>

        <div class="linescore-card white-card">
          <h2>Linescore</h2>
          <div class="table-container">
            <table class="linescore-table">
              <thead>
                <tr>
                  <th class="team-col"></th>
                  <th v-for="inning in game.linescore.innings" :key="inning.num">{{ inning.num }}</th>
                  <th>R</th>
                  <th>H</th>
                  <th>E</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="team-col">{{ game.away_team }}</td>
                  <td v-for="inning in game.linescore.innings" :key="inning.num">{{ inning.away.runs }}</td>
                  <td><strong>{{ game.linescore.teams.away.runs || 0 }}</strong></td>
                  <td><strong>{{ game.linescore.teams.away.hits || 0 }}</strong></td>
                  <td><strong>{{ game.linescore.teams.away.errors || 0 }}</strong></td>
                </tr>
                <tr>
                  <td class="team-col">{{ game.home_team }}</td>
                  <td v-for="inning in game.linescore.innings" :key="inning.num">{{ inning.home.runs }}</td>
                  <td><strong>{{ game.linescore.teams.home.runs || 0 }}</strong></td>
                  <td><strong>{{ game.linescore.teams.home.hits || 0 }}</strong></td>
                  <td><strong>{{ game.linescore.teams.home.errors || 0 }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="boxscore-section">
          <div class="team-boxscore white-card">
            <h2>{{ game.away_team }}</h2>
            <BoxscoreTable :players="awayPlayers" />
          </div>
          <div class="team-boxscore white-card">
            <h2>{{ game.home_team }}</h2>
            <BoxscoreTable :players="homePlayers" />
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import BoxscoreTable from '@/components/BoxscoreTable.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import ErrorDisplay from '@/components/ErrorDisplay.vue';

export default {
  name: 'GameDetailView',
  components: {
    BoxscoreTable,
    LoadingIndicator,
    ErrorDisplay
  },
  data() {
    return {
      gameId: null,
      game: null,
      loading: true,
      error: null,
    };
  },

  computed: {
    awayPlayers() {
      if (!this.game || !this.game.players) return [];
      return this.game.players.away.filter(p => 
        (p.stats.batting && Object.keys(p.stats.batting).length > 0) ||
        (p.stats.pitching && Object.keys(p.stats.pitching).length > 0)
      );
    },
    homePlayers() {
      if (!this.game || !this.game.players) return [];
      return this.game.players.home.filter(p => 
        (p.stats.batting && Object.keys(p.stats.batting).length > 0) ||
        (p.stats.pitching && Object.keys(p.stats.pitching).length > 0)
      );
    }
  },
  async created() {
    this.gameId = this.$route.params.id;
    await this.fetchGameData();
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    async fetchGameData() {
      this.loading = true;
      this.error = null;
      try {
        const response = await ApiService.getGameDetails(this.gameId);
        if (!response.data || !response.data.linescore) {
            throw new Error("Incomplete game data received from API.");
        }
        this.game = response.data;
      } catch (err) {
        console.error("Failed to fetch game data:", err);
        this.error = "Detailed statistics may not be available for games that have not yet started or were canceled.";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.fade-in-enter-active, .fade-in-leave-active { transition: opacity 0.5s ease; }
.fade-in-enter-from, .fade-in-leave-to { opacity: 0; }

.game-detail-view {
  background-color: #f0f2f5;
  padding: 20px 40px;
  min-height: 100vh;
}
.white-card {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  margin-bottom: 25px;
}
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

.game-header { position: relative; }
.header-info { display: flex; justify-content: space-between; color: #6c757d; font-size: 0.9em; margin-bottom: 15px; }
.status { font-weight: bold; text-transform: uppercase; }
.scoreboard { display: flex; justify-content: space-between; align-items: center; }
.team { display: flex; align-items: center; gap: 20px; width: 45%; }
.team.home { justify-content: flex-end; }

.team-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 150px;
  text-align: center;
}

.team-logo { width: 60px; height: 60px; }

.team-name {
  font-size: 1.1em;
  font-weight: 600;
}

.team-score { font-size: 2.8em; font-weight: bold; }
.vs { color: #6c757d; font-weight: bold; font-size: 0.9em; }

.linescore-card h2 { margin: 0 0 20px; }
.table-container {
  overflow-x: auto;
}
.linescore-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
  white-space: nowrap;
}
.linescore-table th, .linescore-table td {
  padding: 12px 10px;
  min-width: 40px;
}
.linescore-table thead th { font-weight: normal; color: #6c757d; border-bottom: 2px solid #dee2e6; }
.linescore-table tbody tr:first-child td { border-bottom: 1px solid #dee2e6; }
.linescore-table .team-col {
  text-align: left;
  font-weight: bold;
  width: 200px;
}
.linescore-table td strong { font-size: 1.1em; }
.linescore-table th:nth-last-child(-n+3), .linescore-table td:nth-last-child(-n+3) {
  border-left: 1px solid #dee2e6;
  font-weight: bold;
  background-color: #f8f9fa;
}

.boxscore-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 25px;
}
.team-boxscore h2 { margin: 0 0 15px; }

@media (min-width: 1200px) {
  .boxscore-section {
    grid-template-columns: 1fr 1fr;
  }
}

.team-info-link {
  text-decoration: none;
  color: inherit;
}
.team-info {
  transition: transform 0.2s ease-in-out;
}
.team-info-link:hover .team-info {
  transform: scale(1.05);
}
</style>