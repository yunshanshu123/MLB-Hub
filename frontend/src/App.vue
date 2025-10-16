<template>
  <div id="app">
    <AppHeader />
    <main class="content">
      <router-view/>
    </main>
  </div>
</template>

<script>
import AppHeader from './components/AppHeader.vue';

export default {
  components: {
    AppHeader
  }
}
</script>

<style>
/* 全局样式 */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #f0f2f5;
  margin: 0;
}
#app {
  max-width: 900px; /* 调整为更适合竖向列表的宽度 */
  margin: 20px auto;
  
}
.content {
  background-color: white;
  padding: 20px;
  border-radius: 0 0 8px 8px; /* 圆角只应用于底部 */
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style>