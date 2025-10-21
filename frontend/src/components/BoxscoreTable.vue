<template>
  <div class="boxscore-table-wrapper">
    <table class="boxscore-table">
      <thead>
        <tr>
          <th>Player</th>
          <th>AB</th>
          <th>R</th>
          <th>H</th>
          <th>RBI</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="player in batters" :key="player.id">
          <td><router-link :to="'/player/' + player.id">{{ player.name }}</router-link></td>
          <td>{{ player.stats.batting.atBats || 0 }}</td>
          <td>{{ player.stats.batting.runs || 0 }}</td>
          <td>{{ player.stats.batting.hits || 0 }}</td>
          <td>{{ player.stats.batting.rbi || 0 }}</td>
        </tr>
      </tbody>
    </table>
    
    <table class="boxscore-table pitching-table">
      <thead>
        <tr>
          <th>Pitcher</th>
          <th>IP</th>
          <th>H</th>
          <th>R</th>
          <th>ER</th>
          <th>BB</th>
          <th>SO</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="player in pitchers" :key="player.id">
          <td><router-link :to="'/player/' + player.id">{{ player.name }}</router-link></td>
          <td>{{ player.stats.pitching.inningsPitched || 0 }}</td>
          <td>{{ player.stats.pitching.hits || 0 }}</td>
          <td>{{ player.stats.pitching.runs || 0 }}</td>
          <td>{{ player.stats.pitching.earnedRuns || 0 }}</td>
          <td>{{ player.stats.pitching.baseOnBalls || 0 }}</td>
          <td>{{ player.stats.pitching.strikeOuts || 0 }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'BoxscoreTable',
  props: {
    players: {
      type: Array,
      required: true
    }
  },
  computed: {
    batters() {
      return this.players.filter(p => p.stats.batting && Object.keys(p.stats.batting).length > 0);
    },
    pitchers() {
      return this.players.filter(p => p.stats.pitching && Object.keys(p.stats.pitching).length > 0);
    }
  }
}
</script>

<style scoped>
.boxscore-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}
.pitching-table {
  margin-top: 20px;
}
.boxscore-table th, .boxscore-table td {
  text-align: left;
  padding: 8px;
  border-bottom: 1px solid #f0f2f5;
}
.boxscore-table th {
  color: #6c757d;
  font-weight: normal;
}
.boxscore-table td a {
  color: #002D72;
  text-decoration: none;
  font-weight: 500;
}
.boxscore-table td a:hover {
  text-decoration: underline;
}
.boxscore-table th:not(:first-child), .boxscore-table td:not(:first-child) {
  text-align: right;
}
</style>