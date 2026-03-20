import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    currentUser: 'Operator', // Default
    users: ['Operator', 'QA'],
    // apiUrl: 'http://localhost:8000/api'
    apiUrl: (import.meta.env.BASE_URL.replace(/\/$/, '') || '') + '/api' // Use proxy with base path
  }),
  actions: {
    setCurrentUser(user) {
      this.currentUser = user
    }
  }
})
