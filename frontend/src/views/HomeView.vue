<template>
  <div class="schedule-view">
    <div class="header">
      <h1>Schedule & Scores</h1>
      <!-- 使用浏览器原生的日期选择器 -->
      <input type="date" v-model="selectedDate" class="date-input">
    </div>
    
    <div v-if="loading" class="loading">Fetching data for {{ formattedDate }}...</div>

    <!-- 模板的其余部分保持不变 -->
    <div v-if="!loading && schedule.length > 0" class="schedule-list">
      <div v-for="game in schedule" :key="game.id" class="game-card">
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
    </div>
    <div v-if="!loading && schedule.length === 0" class="no-games">
      No games scheduled for {{ formattedDate }}.
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService.js';

// 辅助函数：获取今天的日期并格式化为 "YYYY-MM-DD"
function getTodayDateString() {
  const today = new Date();
  return today.toISOString().split('T')[0];
}

export default {
  name: 'HomeView',
  // 不再需要注册 Datepicker 组件
  components: {}, 
  data() {
    return {
      schedule: [],
      loading: true,
      // 关键变化: selectedDate 现在直接存储 "YYYY-MM-DD" 格式的字符串
      selectedDate: getTodayDateString(), 
    };
  },
  computed: {
    // 用于在UI上美化显示日期
    formattedDate() {
      if (!this.selectedDate) return '';
      // 将 "YYYY-MM-DD" 字符串转换为 Date 对象以便格式化
      const date = new Date(this.selectedDate);
      // 加上时区补偿，防止显示成前一天
      const utcDate = new Date(date.valueOf() + date.getTimezoneOffset() * 60000);
      return utcDate.toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric'
      });
    }
  },
  // 关键变化: 对原生元素的 v-model 使用 watch 是最可靠的方式
  watch: {
    selectedDate(newDateStr) {
      if (newDateStr) {
        this.fetchScheduleForDate(newDateStr);
      }
    }
  },
  created() {
    this.fetchScheduleForDate(this.selectedDate);
  },
  methods: {
    async fetchScheduleForDate(dateString) {
      this.loading = true;
      this.schedule = [];
      
      try {
        // 现在 dateString 就是我们需要的 "YYYY-MM-DD" 格式，无需转换
        const response = await ApiService.getSchedule(dateString);
        this.schedule = response.data;
      } catch (error) {
        console.error(`Failed to fetch schedule for ${dateString}:`, error);
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
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    
    /* 为新的原生日期选择器添加样式 */
    .date-input {
      font-family: inherit; /* 继承父元素的字体 */
      font-size: 1rem;
      padding: 8px 12px;
      border: 1px solid #ccc;
      border-radius: 6px;
      width: 180px; /* 给一个合适的宽度 */
    }

    .loading, .no-games { text-align: center; color: #888; padding: 40px 0; font-size: 1.1em; }
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