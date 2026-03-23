import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    currentUser: 'Admin', // Default
    users: ['Operator', 'QA', 'Admin'],
    // Dynamically determine API URL relative to the current base
    apiUrl: (window._APP_BASE_ || '').replace(/\/$/, '') + '/api'
  }),
  actions: {
    setCurrentUser(user) {
      this.currentUser = user
    }
  }
})
