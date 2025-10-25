<template>
  <div class="error-container">
    <h2>{{ title }}</h2>
    <p v-if="message">{{ message }}</p>
    
    <a @click="$emit('goBack')" class="back-link" v-if="showBackButton">
      <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M400-80 0-480l400-400 71 71-329 329 329 329-71 71Z"/></svg>
      <span>Back</span>
    </a>
  </div>
</template>

<script>
export default {
  name: 'ErrorDisplay',
  props: {
    title: {
      type: String,
      default: 'An Error Occurred'
    },
    message: {
      type: String,
      default: 'Could not load the requested data. Please try again later.'
    },
    showBackButton: {
      type: Boolean,
      default: true
    }
  },
  emits: ['goBack']
}
</script>

<style scoped>
.error-container {
  text-align: center;
  padding: 80px 20px;
}
h2 {
  color: #d9534f;
}
p {
  color: #555;
}
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: #fff;
  color: #333;
  padding: 10px 18px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
  cursor: pointer;
  margin-top: 20px;
}
.back-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}
.back-link svg {
  fill: #333;
}
</style>