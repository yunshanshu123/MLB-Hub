import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
  // 让 getSchedule 接受一个日期字符串参数
  getSchedule(dateString) {
    // 如果没有提供日期，就请求 /schedule
    // 如果提供了日期，就请求 /schedule/YYYY-MM-DD
    const url = dateString ? `/schedule/${dateString}` : '/schedule';
    return apiClient.get(url);
  }
};