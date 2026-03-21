import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TemplateEditor from '../views/TemplateEditor.vue'
import DocumentDetail from '../views/DocumentDetail.vue'

const getBasePath = () => {
  let base = window._APP_BASE_ || '/'
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
  history: createWebHistory(getBasePath()),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/templates/new',
      name: 'create-template',
      component: TemplateEditor
    },
    {
      path: '/templates/:id/edit',
      name: 'edit-template',
      component: TemplateEditor
    },
    {
      path: '/documents/:id',
      name: 'document-detail',
      component: DocumentDetail
    }
  ]
})

export default router
