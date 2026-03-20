import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TravelerDetail from '../views/TravelerDetail.vue'
import InstructionDetail from '../views/InstructionDetail.vue'

const router = createRouter({
  history: createWebHistory(), // Remove base url for now or ensure it works
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/traveler/:id',
      name: 'traveler',
      component: TravelerDetail
    },
    {
      path: '/instructions/:id',
      name: 'instructions',
      component: InstructionDetail
    }
  ]
})

export default router
