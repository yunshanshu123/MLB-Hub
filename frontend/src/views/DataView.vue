<template>
  <div class="data-view">
    <h1>Data Search</h1>
    <p class="subtitle">Search for MLB players or teams by name.</p>

    <form @submit.prevent="performSearch" class="search-form">
      <input 
        type="text" 
        v-model="query" 
        placeholder="e.g., Aaron Judge or New York Yankees"
        class="search-input"
        required
      >
      <button type="submit" :disabled="loading || !query.trim()">
        {{ loading ? 'Searching...' : 'Search' }}
      </button>
    </form>

    <div v-if="loading" class="loading-message">
      <div class="spinner"></div>
      Searching the official MLB database...
    </div>

    <transition-group 
      name="card-list" 
      tag="div" 
      class="results-grid"
      v-if="!loading && results.length > 0"
    >
      <div 
        v-for="(item, index) in results" 
        :key="item.id" 
        class="result-card"
        :style="{ 'transition-delay': index * 50 + 'ms' }"
      >
        <div v-if="item.type === 'player'">
          <div class="card-header">Player</div>
          <img :src="item.photo" :alt="item.name" @error="imageError" class="item-photo player-photo">
          <h3 class="item-name">{{ item.name }}</h3>
          <p><strong>Age:</strong> {{ item.age || 'N/A' }}</p>
          <p><strong>Team:</strong> {{ item.team || 'N/A' }}</p>
          <p><strong>Position:</strong> {{ item.position || 'N/A' }}</p>
        </div>

        <div v-if="item.type === 'team'">
          <div class="card-header">Team</div>
          <img :src="item.logo" :alt="item.name" @error="imageError" class="item-photo team-logo">
          <h3 class="item-name">{{ item.name }}</h3>
          <p><strong>Venue:</strong> {{ item.venue || 'N/A' }}</p>
          <p><strong>League:</strong> {{ item.league || 'N/A' }}</p>
          <p><strong>Division:</strong> {{ item.division || 'N/A' }}</p>
        </div>
      </div>
    </transition-group>
    
    <div v-if="!loading && searched && results.length === 0" class="no-results">
      No results found for "{{ lastQuery }}". Please check the spelling or try another name.
    </div>

  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'DataView',
  data() {
    return {
      query: '',
      lastQuery: '',
      results: [],
      loading: false,
      searched: false
    };
  },
  methods: {
    async performSearch() {
      if (!this.query.trim() || this.loading) return;

      this.loading = true;
      this.searched = true;
      this.lastQuery = this.query;
      this.results = [];

      try {
        const response = await ApiService.searchData(this.query);
        this.results = response.data;
      } catch (error) {
        console.error("Failed to perform search:", error);
      } finally {
        this.loading = false;
      }
    },
    imageError(event) {
      event.target.src = 'https://www.mlbstatic.com/team-logos/league/1.svg';
    }
  }
};
</script>

<style scoped>
/* --- 基础样式 --- */
.data-view { text-align: center; }
.subtitle { color: #666; margin-top: -10px; margin-bottom: 30px; }
.search-form { display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; }
.search-input {
  width: 400px;
  padding: 10px 15px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  transition: box-shadow 0.2s;
}
.search-input:focus {
  outline: none;
  border-color: #002D72;
  box-shadow: 0 0 0 3px rgba(0, 45, 114, 0.2);
}
button {
  padding: 10px 20px;
  font-size: 1rem;
  color: white;
  background-color: #002D72;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}
button:hover:not(:disabled) { background-color: #041E42; }
button:disabled { background-color: #aaa; cursor: not-allowed; }
.loading-message { display: flex; align-items: center; justify-content: center; gap: 15px; color: #888; padding: 40px 0; font-size: 1.1em; }
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #ccc;
  border-top-color: #002D72;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.no-results { color: #888; padding: 40px 0; font-size: 1.1em; }
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  text-align: left;
}
.result-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  padding: 15px;
  background-color: #fff;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer; 
}

.result-card:hover {
  transform: translateY(-5px); 
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

.card-header {
  font-size: 0.8em;
  font-weight: bold;
  color: #FA4616;
  text-transform: uppercase;
  margin-bottom: 10px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}
.item-photo {
  display: block;
  margin: 0 auto 15px auto;
  border: 2px solid #f0f0f0;
  background-color: #fff;
}
.player-photo { width: 120px; height: 120px; object-fit: cover; border-radius: 50%; }
.team-logo { width: 100px; height: 100px; object-fit: contain; }
.item-name { text-align: center; margin-bottom: 15px; font-size: 1.2em; }
.result-card p { margin: 5px 0; font-size: 0.95em; }

.card-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.card-list-enter-active {
  transition: all 0.5s ease-out;
}
</style>