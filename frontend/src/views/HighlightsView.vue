<template>
  <div class="highlights-view">
    <h1>MLB Video Highlights</h1>
    <p class="subtitle">Watch the latest highlights and game recaps from the official MLB channel.</p>

    <form @submit.prevent="performSearch" class="search-form">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search for videos (e.g., walk-off, grand slam)..."
        class="search-input"
        @keyup.enter="performSearch"
      >
      <button type="submit" :disabled="loading">
        {{ loading ? 'Searching...' : 'Search' }}
      </button>
    </form>
    
    <div class="content-container">

      <div v-if="loading" class="loading-state-container">
        <LoadingIndicator :message="isInitialLoading ? 'Loading latest videos...' : 'Searching for results...'" />
      </div>

      <ErrorDisplay v-if="!loading && error" :message="error" />

      <div v-if="!loading && !error" class="video-content-wrapper">
        <div class="results-info" v-if="videos.length > 0">
          <h2 v-if="lastSearchQuery">Results for: "{{ lastSearchQuery }}"</h2>
          <h2 v-else>Latest Videos</h2>
        </div>

        <div v-if="videos.length === 0" class="no-results-container">
          <p>No videos found. Please try a different search term.</p>
        </div>

        <transition-group name="card-list" tag="div" class="video-grid">
          <a v-for="(video, index) in videos" 
            :key="video.videoId" 
            :href="'https://www.youtube.com/watch?v=' + video.videoId" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="video-card-link"
            :style="{ 'transition-delay': index * 50 + 'ms' }">
            <div class="video-card">
              <img :src="video.thumbnailUrl" :alt="video.title" class="video-thumbnail">
              <div class="video-info">
                <h3 class="video-title">{{ video.title }}</h3>
                <span class="video-date">{{ formatDate(video.publishedAt) }}</span>
              </div>
            </div>
          </a>
        </transition-group>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import ErrorDisplay from '@/components/ErrorDisplay.vue';

export default {
  name: 'HighlightsView',
  components: {
    LoadingIndicator,
    ErrorDisplay
  },
  data() {
    return {
      videos: [],
      loading: true,
      isInitialLoading: true,
      error: null,
      searchQuery: '',
      lastSearchQuery: null
    };
  },
  created() {
    this.fetchHighlights(null);
  },
  methods: {
    async fetchHighlights(query) {
      this.loading = true;
      this.error = null;

      try {
        const response = await ApiService.getHighlights(query);

        this.videos = response.data;
        this.lastSearchQuery = query;

      } catch (err) {
        console.error("Failed to fetch videos:", err);
        this.error = err.response?.data?.error || "Could not connect to the video service.";
        this.videos = []; 
      } finally {
        this.loading = false;
        this.isInitialLoading = false;
      }
    },
    performSearch() {
      const trimmedQuery = this.searchQuery.trim();
      if (trimmedQuery !== (this.lastSearchQuery || '')) {
        this.fetchHighlights(trimmedQuery || null);
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString('en-US', options);
    }
  }
};
</script>

<style scoped>
.content-container {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.loading-state-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-grow: 1; 
  padding: 50px 0;
}

.highlights-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 { text-align: center; }
.subtitle { text-align: center; margin-bottom: 30px; color: #666; }
.search-form { display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; }
.search-input { width: 50%; max-width: 500px; padding: 10px 15px; font-size: 1rem; border: 1px solid #ccc; border-radius: 6px; }
.search-form button { padding: 10px 20px; font-size: 1rem; color: white; background-color: #002D72; border: none; border-radius: 6px; cursor: pointer; min-width: 120px; transition: background-color 0.2s; }
.search-form button:disabled { background-color: #a0a0a0; cursor: not-allowed; }
.results-info h2 { text-align: center; font-size: 1.5em; margin-bottom: 20px; color: #333; }
.no-results-container { text-align: center; padding: 40px 20px; color: #888; font-size: 1.1em; }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.video-card-link { text-decoration: none; color: inherit; }
.video-card { background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: all 0.3s ease; display: flex; flex-direction: column; }
.video-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
.video-thumbnail { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; display: block; background-color: #eee; }
.video-info { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; }
.video-title { font-size: 1.1em; margin: 0 0 10px; line-height: 1.4; flex-grow: 1; }
.video-date { font-size: 0.85em; color: #888; margin-top: auto; }

.card-list-enter-from { opacity: 0; transform: translateY(20px); }
.card-list-leave-to { opacity: 0; transform: translateY(20px); } 
.card-list-enter-active, .card-list-leave-active { transition: all 0.5s ease-out; }

</style>