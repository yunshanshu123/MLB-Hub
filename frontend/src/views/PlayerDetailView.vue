<template>
  <div class="player-detail-view">
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading Player Data...</p>
    </div>

    <div v-if="error" class="error-container">
      <h2>Could not load player data.</h2>
      <p>{{ error }}</p>
      <a @click="goBack" class="back-link">← Go Back</a>
    </div>

    <transition name="fade-in">
      <div v-if="!loading && !error && player" class="player-content">
        <div class="player-header-background"></div>
        <div class="player-header">
          <img :src="player.photo" :alt="player.name" class="player-photo-large">
          <div class="player-info">
            <span class="jersey-number">#{{ player.jerseyNumber }}</span>
            <h1>{{ player.name }}</h1>
            <div class="player-bio">
              <span>{{ player.team || 'N/A' }}</span>
              <span> • </span>
              <span>Pos: {{ player.position || 'N/A' }}</span>
              <span> • </span>
              <span>Age: {{ player.age || 'N/A' }}</span>
              <span> • </span>
              <span>Born: {{ player.birthDate || 'N/A' }}</span>
            </div>
          </div>
          <a @click="goBack" class="back-link header-back-link">← Back</a>
        </div>

        <div class="stats-section">
          <div class="stats-controls">
            <div class="season-selector">
              <label for="season-select">Season:</label>
              <select id="season-select" v-model="selectedSeason">
                <option v-for="season in availableSeasons" :key="season" :value="season">
                  {{ season }}
                </option>
              </select>
            </div>
            <div class="stats-tabs" v-if="hasHittingStats && hasPitchingStats">
              <button :class="{ active: statsView === 'hitting' }" @click="statsView = 'hitting'">Hitting</button>
              <button :class="{ active: statsView === 'pitching' }" @click="statsView = 'pitching'">Pitching</button>
            </div>
          </div>

          <div v-if="selectedSeasonStats" class="stats-card">
            <transition name="fade-in" mode="out-in">
              <div v-if="statsView === 'hitting' && hasHittingStats" class="stats-grid-container">
                <h2>Hitting Stats ({{ selectedSeason }})</h2>
                <div class="stats-grid">
                    <div class="stat-item"><span>Team</span><strong>{{ selectedSeasonStats.hitting.team_name }}</strong></div>
                    <div class="stat-item"><span>AVG</span><strong>{{ selectedSeasonStats.hitting.avg }}</strong></div>
                    <div class="stat-item"><span>HR</span><strong>{{ selectedSeasonStats.hitting.homeRuns }}</strong></div>
                    <div class="stat-item"><span>RBI</span><strong>{{ selectedSeasonStats.hitting.rbi }}</strong></div>
                    <div class="stat-item"><span>OPS</span><strong>{{ selectedSeasonStats.hitting.ops }}</strong></div>
                    <div class="stat-item"><span>Hits</span><strong>{{ selectedSeasonStats.hitting.hits }}</strong></div>
                    <div class="stat-item"><span>Runs</span><strong>{{ selectedSeasonStats.hitting.runs }}</strong></div>
                    <div class="stat-item"><span>SB</span><strong>{{ selectedSeasonStats.hitting.stolenBases }}</strong></div>
                </div>
              </div>
              <div v-else-if="statsView === 'pitching' && hasPitchingStats" class="stats-grid-container">
                <h2>Pitching Stats ({{ selectedSeason }})</h2>
                <div class="stats-grid">
                  <div class="stat-item"><span>Team</span><strong>{{ selectedSeasonStats.pitching.team_name }}</strong></div>
                  <div class="stat-item"><span>W-L</span><strong>{{ selectedSeasonStats.pitching.wins }}-{{ selectedSeasonStats.pitching.losses }}</strong></div>
                  <div class="stat-item"><span>ERA</span><strong>{{ selectedSeasonStats.pitching.era }}</strong></div>
                  <div class="stat-item"><span>SO</span><strong>{{ selectedSeasonStats.pitching.strikeOuts }}</strong></div>
                  <div class="stat-item"><span>IP</span><strong>{{ selectedSeasonStats.pitching.inningsPitched }}</strong></div>
                  <div class="stat-item"><span>WHIP</span><strong>{{ selectedSeasonStats.pitching.whip }}</strong></div>
                  <div class="stat-item"><span>Saves</span><strong>{{ selectedSeasonStats.pitching.saves }}</strong></div>
                  <div class="stat-item"><span>BAA</span><strong>{{ selectedSeasonStats.pitching.avg }}</strong></div>
                </div>
              </div>
            </transition>
          </div>
          <div v-else class="no-stats-info">
            <p>No statistical data available for the selected season.</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'PlayerDetailView',
  data() {
    return {
      playerId: null,
      player: null,
      stats: {},
      selectedSeason: null,
      statsView: 'hitting',
      loading: true,
      error: null,
    };
  },
  computed: {
    availableSeasons() {
      return Object.keys(this.stats).sort((a, b) => b - a);
    },
    selectedSeasonStats() {
      return this.stats[this.selectedSeason] || null;
    },
    hasHittingStats() {
      return this.selectedSeasonStats && this.selectedSeasonStats.hitting;
    },
    hasPitchingStats() {
      return this.selectedSeasonStats && this.selectedSeasonStats.pitching;
    }
  },
  async created() {
    this.playerId = this.$route.params.id;
    await this.fetchPlayerData();
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    async fetchPlayerData() {
      this.loading = true;
      this.error = null;
      try {
        const [detailsResponse, statsResponse] = await Promise.all([
          ApiService.getPlayerDetails(this.playerId),
          ApiService.getPlayerStats(this.playerId)
        ]);

        this.player = detailsResponse.data;
        this.stats = statsResponse.data;

        if (this.availableSeasons.length > 0) {
          this.selectedSeason = this.availableSeasons[0];
          if (this.hasHittingStats) {
            this.statsView = 'hitting';
          } else if (this.hasPitchingStats) {
            this.statsView = 'pitching';
          }
        }
      } catch (err) {
        console.error("Failed to fetch player data:", err);
        this.error = err.response?.data?.error || "An unknown error occurred.";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* --- 整体动画 --- */
.fade-in-enter-active, .fade-in-leave-active { transition: opacity 0.5s ease; }
.fade-in-enter-from, .fade-in-leave-to { opacity: 0; }

.player-detail-view { background-color: #f0f2f5; min-height: 100vh; }
.loading-container, .error-container { text-align: center; padding: 80px 20px; }
.spinner { width: 40px; height: 40px; border: 4px solid #ccc; border-top-color: #002D72; border-radius: 50%; margin: 0 auto 20px; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* --- 头部样式 --- */
.player-header-background {
  height: 200px;
  background: linear-gradient(to right, #002D72, #041E42);
  border-radius: 0 0 20px 20px;
}
.player-header {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  padding: 0 40px;
  margin-top: -100px;
  position: relative;
  margin-bottom: 30px;
}
.player-photo-large {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  object-fit: cover;
  border: 6px solid #f0f2f5;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
  background-color: #fff;
}
.player-info { color: white; padding-bottom: 15px; }
.jersey-number { font-size: 1.5em; font-weight: bold; color: rgba(255, 255, 255, 0.7); }
.player-info h1 { margin: 0; font-size: 3em; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
/* ↓↓↓ 关键改动：将透明度从 0.9 改为 0.95，使其更不透明、更清晰 ↓↓↓ */
.player-bio { display: flex; gap: 8px; color: rgba(255, 255, 255, 0.95); margin-top: 5px; font-weight: 500;}

.back-link {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: background-color 0.3s;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.back-link:hover { background-color: rgba(255, 255, 255, 0.2); }
.header-back-link { position: absolute; top: -80px; right: 40px; padding: 8px 15px; font-size: 0.9em; }
.error-container .back-link { margin-top: 20px; padding: 10px 20px; color: #333; background-color: #e9ecef; border: none; }

/* --- 统计板块样式 --- */
.stats-section { padding: 0 40px; }
.stats-controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.season-selector { display: flex; align-items: center; gap: 10px; }
.season-selector label { font-weight: bold; }
.season-selector select {
  font-size: 1em;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
.stats-tabs { display: flex; background-color: #e9ecef; border-radius: 8px; padding: 4px; }
.stats-tabs button {
  padding: 8px 20px;
  font-size: 1em;
  border: none;
  background-color: transparent;
  color: #555;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}
.stats-tabs button.active { background-color: #fff; color: #002D72; font-weight: bold; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

.stats-card { background: #fff; border-radius: 12px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.stats-card h2 { margin: 0 0 20px; font-size: 1.5em; color: #333; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 20px; }

.stat-item {
  text-align: center;
  padding: 15px 10px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}
.stat-item span {
  display: block;
  font-size: 0.85em;
  color: #6c757d;
  margin-bottom: 8px;
  text-transform: uppercase;
  font-weight: 600;
}
.stat-item strong {
  display: block;
  font-size: 1.6em;
  color: #002D72;
  font-weight: 700;
  line-height: 1.2;
}
.no-stats-info { text-align: center; color: #888; padding: 40px 0; background-color: #fff; border-radius: 12px; }
</style>