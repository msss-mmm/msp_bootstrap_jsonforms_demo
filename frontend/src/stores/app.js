import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    currentUser: 'Operator', // Default
    users: ['Operator', 'QA'],
    // apiUrl: 'http://localhost:8000/api'
    apiUrl: '/api' // Use proxy
  }),
  actions: {
    setCurrentUser(user) {
      this.currentUser = user
    }
  }
})
