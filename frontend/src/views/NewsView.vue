<template>
  <div class="news-view">
    <h1>Latest MLB News</h1>
    <p class="subtitle">Stay updated with the latest headlines from around the league.</p>

    <LoadingIndicator v-if="loading && articles.length === 0" message="Loading news..." />
    <ErrorDisplay v-if="error" :message="error" :showBackButton="false" />

    <transition-group name="card-list" tag="div" class="news-list">
      <a v-for="(article, index) in articles" 
         :key="article.id + '-' + index" 
         :href="article.url" 
         target="_blank" 
         rel="noopener noreferrer" 
         class="article-card-link"
         :style="{ 'transition-delay': index * 50 + 'ms' }">
        <div class="article-card">
          <img v-if="article.thumbnail" :src="article.thumbnail" :alt="article.title" class="article-thumbnail" @error="handleImageError">
          <div class="article-content">
            <h2 class="article-title">{{ article.title }}</h2>
            <p class="article-summary" v-html="article.summary"></p>
            <span class="article-date">{{ formatDate(article.date) }}</span>
          </div>
        </div>
      </a>
    </transition-group>

    <div class="load-more-container" v-if="!error">
      <button @click="loadMoreNews" v-if="hasMore" :disabled="loading" class="load-more-button">
        {{ loading ? 'Loading...' : 'Load More News' }}
      </button>
      <p v-if="!hasMore && articles.length > 0" class="no-more-news">
        You've reached the end of the news.
      </p>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import ErrorDisplay from '@/components/ErrorDisplay.vue';
import MlbLogo from '@/assets/mlb-logo.jpg';

export default {
  name: 'NewsView',
  components: {
    LoadingIndicator,
    ErrorDisplay
  },
  data() {
    return {
      articles: [],
      loading: false,
      error: null,
      fallbackImage: MlbLogo,
      currentPage: 1,
      hasMore: true 
    };
  },
  created() {
    this.fetchNews(); 
  },
  methods: {
    async fetchNews() {
      if (this.loading) return; 
      this.loading = true;
      this.error = null;
      try {
        const response = await ApiService.getNews(this.currentPage);
        this.articles = [...this.articles, ...response.data.articles];
        this.hasMore = response.data.hasMore;
      } catch (err) {
        console.error("Failed to fetch news:", err);
        this.error = err.response?.data?.error || "Could not connect to the news service.";
      } finally {
        this.loading = false;
      }
    },
    loadMoreNews() {
      if (this.hasMore) {
        this.currentPage += 1;
        this.fetchNews();
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return new Date(dateString).toLocaleDateString('en-US', options);
    },
    handleImageError(event) {
      event.target.src = this.fallbackImage;
      event.target.onerror = null; 
      event.target.classList.add('is-fallback');
    }
  }
};
</script>

<style scoped>
.news-view {
  max-width: 900px;
  margin: 0 auto;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.article-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.article-card {
  display: flex;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

.article-thumbnail {
  width: 200px;
  height: auto;
  min-height: 150px;
  object-fit: cover;
  flex-shrink: 0;
  background-color: #fff;
}

.article-thumbnail.is-fallback {
  object-fit: contain; 
  padding: 20px;       
  background-color: #f0f2f5; 
}

.article-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.article-title {
  margin: 0 0 10px;
  font-size: 1.3em;
  color: #002D72;
}

.article-summary {
  margin: 0 0 15px;
  color: #555;
  line-height: 1.6;
  flex-grow: 1; 
}

.article-date {
  font-size: 0.85em;
  color: #888;
  align-self: flex-start; 
}

.card-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.card-list-enter-active {
  transition: all 0.5s ease-out;
}
.load-more-container {
  text-align: center;
  margin-top: 30px;
  padding: 20px 0;
}
.load-more-button {
  background-color: #002D72;
  color: white;
  border: none;
  padding: 12px 25px;
  font-size: 1.1em;
  font-weight: bold;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.load-more-button:hover:not(:disabled) {
  background-color: #041E42;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.load-more-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.no-more-news {
  color: #888;
  font-weight: 500;
}
</style>