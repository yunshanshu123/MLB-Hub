import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
  getSchedule(dateString) {
    const url = dateString ? `/schedule/${dateString}` : '/schedule';
    return apiClient.get(url);
  },

  searchData(query) {
    return apiClient.get('/search', { 
      params: { 
        q: query 
      } 
    });
  }
};