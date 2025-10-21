import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DataView from '../views/DataView.vue'
import PlayerDetailView from '../views/PlayerDetailView.vue'
import TeamDetailView from '../views/TeamDetailView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/data', name: 'data', component: DataView },
  { path: '/player/:id', name: 'playerDetail', component: PlayerDetailView },
  {
    path: '/team/:id',
    name: 'teamDetail',
    component: TeamDetailView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router