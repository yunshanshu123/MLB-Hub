<template>
  <header class="app-header">
    <router-link to="/" class="logo-link">
      <div class="logo">
        <img src="@/assets/mlb-logo.jpg" alt="MLB Hub Logo" class="header-logo">
        <span>MLB Hub</span>
      </div>
    </router-link>
    
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

.logo-link {
  text-decoration: none;
  color: inherit;
  transition: opacity 0.2s ease-in-out;
}

.logo-link:hover {
  opacity: 0.85;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.5em;
  font-weight: bold;
}

.header-logo {
  height: 35px;
  width: auto;
  margin-right: 12px;
}

.navigation a {
  position: relative; 
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

.navigation a.router-link-exact-active::before {
  content: '⚾'; 
  position: absolute; 
  left: -22px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;

  animation: pop-in 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes pop-in {
  0% {
    transform: translateY(-50%) scale(0);
    opacity: 0;
  }
  100% {
    transform: translateY(-50%) scale(1);
    opacity: 1;
  }
}
</style>