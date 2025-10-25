<template>
  <div class="data-view">
    <div class="search-background">
      <div 
        v-for="(image, index) in backgroundImages" 
        :key="index"
        :class="['background-image', { active: currentBackground === index }]"
        :style="{ backgroundImage: `url(${getImageUrl(image)})` }"
      ></div>
    </div>

    <div class="search-container">
      <h1>Data Search</h1>
      <p class="subtitle">Search for MLB players or teams by name, or browse league leaders below.</p>

      <form @submit.prevent="performSearch" class="search-form">
        <div class="search-input-wrapper">
          <input 
            type="text" 
            v-model="query" 
            placeholder="e.g., Aaron Judge or New York Yankees"
            class="search-input"
          >
          <button type="button" v-if="query" @click="clearSearch" class="clear-button">×</button>
        </div>
        <button type="submit" :disabled="loading || !query.trim()">
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </form>
    </div>
    
    <hr class="divider">

    <div v-if="!isSearching" class="leaderboards-section">
      <h2>League Leaders (Regular Season)</h2>
      <div v-if="leadersLoading" class="loading-message">
        <div class="spinner"></div> Loading leaders...
      </div>
      <div v-if="leadersError" class="error-message">
        Could not load league leaders. Please try refreshing the page.
      </div>
      <div v-if="!leadersLoading && !leadersError && leaders" class="leaderboards-content">
        <div class="leaderboard-tabs">
          <button :class="{ active: leaderboardView === 'hitting' }" @click="leaderboardView = 'hitting'">Hitting</button>
          <button :class="{ active: leaderboardView === 'pitching' }" @click="leaderboardView = 'pitching'">Pitching</button>
        </div>
        <transition name="fade-in" mode="out-in">
          <div v-if="leaderboardView === 'hitting'" class="leaderboard-grid">
            <div class="leaderboard-card" v-for="(players, stat) in leaders.hitting" :key="stat">
              <h4>{{ statAliases[stat] || stat }}</h4>
              <ol class="leaderboard-list">
                <li v-for="player in players" :key="player.id" :class="getRankClass(player.rank)">
                  <router-link :to="'/player/' + player.id" class="player-link">
                    <span class="player-rank">{{ player.rank }}</span>
                    <span class="player-name">{{ player.name }}</span>
                    <span class="player-value">{{ player.value }}</span>
                  </router-link>
                </li>
              </ol>
            </div>
          </div>
          <div v-else-if="leaderboardView === 'pitching'" class="leaderboard-grid">
             <div class="leaderboard-card" v-for="(players, stat) in leaders.pitching" :key="stat">
              <h4>{{ statAliases[stat] || stat }}</h4>
              <ol class="leaderboard-list">
                <li v-for="player in players" :key="player.id" :class="getRankClass(player.rank)">
                  <router-link :to="'/player/' + player.id" class="player-link">
                    <span class="player-rank">{{ player.rank }}</span>
                    <span class="player-name">{{ player.name }}</span>
                    <span class="player-value">{{ player.value }}</span>
                  </router-link>
                </li>
              </ol>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <div v-else class="search-results-section">
      <div v-if="loading" class="loading-message">
        <div class="spinner"></div> Searching...
      </div>
      <transition-group 
        name="card-list" tag="div" class="results-grid"
        v-if="!loading && results.length > 0"
      >
        <div v-for="(item, index) in results" :key="item.id" :style="{ 'transition-delay': index * 50 + 'ms' }">
          <router-link v-if="item.type === 'player'" :to="'/player/' + item.id.split('-')[1]" class="card-link">
            <div class="result-card">
              <div class="card-header">Player</div>
              <img :src="item.photo" :alt="item.name" @error="imageError" class="item-photo player-photo">
              <h3 class="item-name">{{ item.name }}</h3>
              <p><strong>Age:</strong> {{ item.age || 'N/A' }}</p><p><strong>Team:</strong> {{ item.team || 'N/A' }}</p><p><strong>Position:</strong> {{ item.position || 'N/A' }}</p>
            </div>
          </router-link>
          <router-link v-if="item.type === 'team'" :to="'/team/' + item.id.split('-')[1]" class="card-link">
            <div class="result-card">
              <div class="card-header">Team</div>
              <img :src="item.logo" :alt="item.name" @error="imageError" class="item-photo team-logo">
              <h3 class="item-name">{{ item.name }}</h3>
              <p><strong>Venue:</strong> {{ item.venue || 'N/A' }}</p><p><strong>League:</strong> {{ item.league || 'N/A' }}</p><p><strong>Division:</strong> {{ item.division || 'N/A' }}</p>
            </div>
          </router-link>
        </div>
      </transition-group>
      <div v-if="!loading && results.length === 0 && searched" class="no-results">
        No results found for "{{ lastQuery }}".
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'DataView',
  data() {
    return {
      query: '', lastQuery: '', results: [],
      loading: false, searched: false,
      leaders: null, leadersLoading: true, leadersError: null,
      leaderboardView: 'hitting', isSearching: false,
      statAliases: {
        homeRuns: 'Home Runs', battingAverage: 'Batting Avg', runsBattedIn: 'RBI',
        onBasePlusSlugging: 'OPS', hits: 'Hits', runs: 'Runs',
        earnedRunAverage: 'ERA', wins: 'Wins', strikeouts: 'Strikeouts',
        walksAndHitsPerInningPitched: 'WHIP', saves: 'Saves', inningsPitched: 'Innings'
      },
      backgroundImages: [
        'Ohtanihitter.jpg',
        'Judge.jpg',
        'Raleigh.jpg',
        'Schwarber.jpg',
        'Ohtanipitcher.jpg',
        'Skenes.jpg',
        'Skubal.jpg',
        'Snell.jpg'
      ],
      currentBackground: 0,
      backgroundInterval: null
    };
  },
  created() {
    this.fetchLeaders();
    
    const queryFromUrl = this.$route.query.q;
    if (queryFromUrl) {
      this.query = queryFromUrl;
      this.performSearch();
    }
  },
  mounted() {
    this.startBackgroundRotation();
  },
  beforeUnmount() {
    this.stopBackgroundRotation();
  },
  methods: {
    async performSearch() {
      const trimmedQuery = this.query.trim();
      if (!trimmedQuery || this.loading) return;

      this.isSearching = true; this.loading = true; this.searched = true;
      this.lastQuery = trimmedQuery; this.results = [];

      if (this.$route.query.q !== trimmedQuery) {
        this.$router.replace({ query: { q: trimmedQuery } });
      }

      try {
        const response = await ApiService.searchData(trimmedQuery);
        this.results = response.data;
      } catch (error) { 
        console.error("Failed to perform search:", error); 
      } 
      finally { this.loading = false; }
    },
    clearSearch() {
      this.query = ''; this.isSearching = false;
      this.searched = false; this.results = [];
      
      if (this.$route.query.q) {
        this.$router.replace({ query: {} });
      }
    },
    async fetchLeaders() {
      this.leadersLoading = true; this.leadersError = null;
      try {
        const response = await ApiService.getLeagueLeaders();
        this.leaders = response.data;
      } catch (error) { console.error("Failed to fetch league leaders:", error); this.leadersError = true; } 
      finally { this.leadersLoading = false; }
    },
    getRankClass(rank) {
      if (rank === 1) return 'rank-gold';
      if (rank === 2) return 'rank-silver';
      if (rank === 3) return 'rank-bronze';
      return 'rank-normal';
    },
    imageError(event) { event.target.src = 'https://www.mlbstatic.com/team-logos/league/1.svg'; },
    
    getImageUrl(imageName) {
      return require(`@/assets/background/${imageName}`);
    },
    startBackgroundRotation() {
      this.backgroundInterval = setInterval(() => {
        this.currentBackground = (this.currentBackground + 1) % this.backgroundImages.length;
      }, 5000);
    },
    stopBackgroundRotation() {
      if (this.backgroundInterval) {
        clearInterval(this.backgroundInterval);
        this.backgroundInterval = null;
      }
    }
  }
};
</script>

<style scoped>
.data-view {
  position: relative;
  min-height: 100vh;
}

.search-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 60vh;
  max-height: 600px;
  min-height: 400px;
  overflow: hidden;
  z-index: 0;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center 20%; 
  background-repeat: no-repeat;
  opacity: 0;
  transition: opacity 1.5s ease-in-out;
}

.background-image.active {
  opacity: 0.6; 
}

.search-container {
  position: relative;
  width: 100%;
  height: 60vh;
  max-height: 600px;
  min-height: 400px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

h1 {
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  margin: 0; 
  text-align: center; 
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  margin: 10px 0 30px 0; 
  text-align: center; 
}

.search-form {
  display: flex;
  justify-content: center;
  gap: 10px;
  align-items: flex-start;
}

.fade-in-enter-active, .fade-in-leave-active { transition: opacity 0.3s ease; }
.fade-in-enter-from, .fade-in-leave-to { opacity: 0; }

.search-input-wrapper {
  position: relative;
  display: inline-block;
}

.search-input { 
  width: 400px; 
  padding: 10px 40px 10px 15px;
  font-size: 1rem; 
  border: 1px solid #ccc; 
  border-radius: 6px; 
}

.clear-button { 
  position: absolute; 
  right: 5px;
  top: 50%; 
  transform: translateY(-50%); 
  background: transparent; 
  border: none; 
  font-size: 1.5em; 
  color: #aaa; 
  cursor: pointer; 
  padding: 0 10px; 
  height: 100%;
}
.clear-button:hover { color: #333; }

.leaderboards-section,
.search-results-section {
  margin-top: 40px;
  padding: 0 20px 40px;
}

.leaderboards-section h2 { text-align: center; margin-bottom: 20px; }
.leaderboard-tabs { display: flex; justify-content: center; margin-bottom: 20px; background-color: #e9ecef; border-radius: 8px; padding: 4px; width: fit-content; margin-left: auto; margin-right: auto; }
.leaderboard-tabs button { padding: 8px 25px; font-size: 1.1em; border: none; background-color: transparent; color: #555; border-radius: 6px; cursor: pointer; transition: all 0.3s; font-weight: 500; }
.leaderboard-tabs button.active { background-color: #fff; color: #002D72; font-weight: bold; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.leaderboard-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.leaderboard-card { background: #fff; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; }
.leaderboard-card h4 { margin: 0 0 10px; font-size: 1.1em; text-align: center; }
.leaderboard-list { list-style: none; padding: 0; margin: 0; }
.leaderboard-list li { border-bottom: 1px solid #f1f1f1; }
.leaderboard-list li:last-child { border-bottom: none; }
.player-link { display: flex; align-items: center; text-decoration: none; color: #333; padding: 8px 4px; border-radius: 4px; transition: background-color 0.2s; }
.player-link:hover { background-color: #f0f2f5; }
.player-rank { font-weight: bold; width: 25px; text-align: center; margin-right: 10px; }
.player-name { flex-grow: 1; font-size: 0.95em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.player-value { font-weight: bold; padding-left: 10px; }

.rank-gold .player-rank { color: #D4AF37; }
.rank-silver .player-rank { color: #C0C0C0; }
.rank-bronze .player-rank { color: #CD7F32; }
.rank-normal .player-rank { color: #6c757d; }

.divider { border: none; border-top: 1px solid #e0e0e0; margin: 0; }
.loading-message { display: flex; align-items: center; justify-content: center; gap: 15px; color: #888; padding: 20px 0; font-size: 1.1em; }
.error-message { text-align: center; color: #d9534f; padding: 20px 0; }
.spinner { width: 24px; height: 24px; border: 3px solid #ccc; border-top-color: #002D72; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.data-view { text-align: center; }
button[type="submit"] { padding: 10px 20px; font-size: 1rem; color: white; background-color: #002D72; border: none; border-radius: 6px; cursor: pointer; }
.no-results { color: #888; padding: 40px 0; font-size: 1.1em; }
.results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; text-align: left; }
.card-link { text-decoration: none; color: inherit; }
.result-card { border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); padding: 15px; background-color: #fff; transition: transform 0.3s ease, box-shadow 0.3s ease; cursor: pointer; }
.result-card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
.card-header { font-size: 0.8em; font-weight: bold; color: #FA4616; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
.item-photo { display: block; margin: 0 auto 15px auto; border: 2px solid #f0f0f0; background-color: #fff; }
.player-photo { width: 120px; height: 120px; object-fit: cover; border-radius: 50%; }
.team-logo { width: 100px; height: 100px; object-fit: contain; }
.item-name { text-align: center; margin-bottom: 15px; font-size: 1.2em; }
.result-card p { margin: 5px 0; font-size: 0.95em; }
.card-list-enter-from { opacity: 0; transform: translateY(20px); }
.card-list-enter-active { transition: all 0.5s ease-out; }
</style>