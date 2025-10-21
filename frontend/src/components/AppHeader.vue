<template>
  <header class="app-header">
    <div class="logo">
      ⚾ MLB Hub
    </div>
    <nav class="navigation">
      <router-link to="/">Schedule</router-link>
      <router-link to="/data">Data</router-link>
      <router-link to="/news">News</router-link>
      <router-link to="/highlights">Highlights</router-link>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'AppHeader'
}
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #002D72;
  color: white;
  padding: 10px 20px;
  border-radius: 8px 8px 0 0;
}

.logo {
  font-size: 1.5em;
  font-weight: bold;
}

.navigation a {
  color: white;
  text-decoration: none;
  margin-left: 20px;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.navigation a:hover {
  background-color: #041E42;
}

.navigation a.router-link-exact-active {
  background-color: #FA4616;
}
</style>