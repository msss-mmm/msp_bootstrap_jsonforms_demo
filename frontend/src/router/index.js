import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TravelerDetail from '../views/TravelerDetail.vue'
import InstructionDetail from '../views/InstructionDetail.vue'

// Dynamically determine the base path at runtime
const getBasePath = () => {
  // Always prioritize the window._APP_BASE_ set in index.html
  let base = window._APP_BASE_ || '/'

  // Ensure it's a valid path for createWebHistory
  // It should be a full path from the root, e.g., / or /mes/
  if (base.startsWith('http')) {
    try {
      base = new URL(base).pathname
    } catch (e) {
      base = '/'
    }
  }

  if (!base.endsWith('/')) {
    base += '/'
  }

  return base
}

const router = createRouter({
  // Use the dynamically detected base path
  history: createWebHistory(getBasePath()),
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
