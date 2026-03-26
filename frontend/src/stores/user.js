import { defineStore } from 'pinia'
import api from '../utils/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || '',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    isManager: (state) => ['admin', 'manager'].includes(state.user?.role),
  },
  actions: {
    async login(username, password) {
      const { data } = await api.post('/auth/login', { username, password })
      this.token = data.access_token
      localStorage.setItem('token', data.access_token)
      await this.fetchUser()
    },
    async fetchUser() {
      const { data } = await api.get('/auth/me')
      this.user = data
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    },
  },
})
