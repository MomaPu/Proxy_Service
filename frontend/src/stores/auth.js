import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api/v1'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    myVM: null,
    ws: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    getUser: (state) => state.user,
    getVM: (state) => state.myVM
  },

  actions: {
    async register(email, password, confirmPassword) {
      try {
        const response = await axios.post(`${API_URL}/auth/register`, {
          email,
          password,
          confirm_password: confirmPassword
        })
        return { success: true, message: response.data.message }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail || 'Registration failed' }
      }
    },

    async login(email, password) {
      try {
        const response = await axios.post(`${API_URL}/auth/login`, { email, password })
        this.token = response.data.access_token
        localStorage.setItem('token', this.token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        await this.fetchProfile()
        await this.fetchMyVM()
        this.connectWebSocket()
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail || 'Login failed' }
      }
    },

    async fetchProfile() {
      try {
        const response = await axios.get(`${API_URL}/profile/me`, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.user = response.data
      } catch (error) {
        console.error('Failed to fetch profile', error)
      }
    },

    async fetchMyVM() {
      try {
        const response = await axios.get(`${API_URL}/profile/my-vm`, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.myVM = response.data
      } catch (error) {
        this.myVM = null
      }
    },

    async changePassword(oldPassword, newPassword) {
      try {
        await axios.post(`${API_URL}/profile/change-password`, {
          old_password: oldPassword,
          new_password: newPassword
        }, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        return { success: true, message: 'Password changed successfully' }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail || 'Failed to change password' }
      }
    },

    async refreshKey() {
      try {
        await axios.post(`${API_URL}/activate/refresh-key`, {}, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        return { success: true, message: 'New activation key sent to your email' }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail || 'Failed to refresh key' }
      }
    },

    async disconnect() {
      try {
        await axios.post(`${API_URL}/activate/disconnect`, {}, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.myVM = null
        return { success: true, message: 'Disconnected from proxy' }
      } catch (error) {
        return { success: false, message: error.response?.data?.detail || 'Failed to disconnect' }
      }
    },

    connectWebSocket() {
      if (!this.token || !this.user) return

      const wsUrl = `ws://localhost:8000/ws/status/${this.user.id}`
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => console.log('WebSocket connected')
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        console.log('WebSocket:', data)
      }
      this.ws.onerror = (error) => console.error('WebSocket error:', error)
      this.ws.onclose = () => console.log('WebSocket disconnected')
    },

    logout() {
      if (this.ws) this.ws.close()
      this.token = null
      this.user = null
      this.myVM = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
  }
})