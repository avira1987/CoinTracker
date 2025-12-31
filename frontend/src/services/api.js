/**
 * سرویس API برای ارتباط با Backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor برای مدیریت خطاها
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // در صورت خطای احراز هویت، به صفحه لاگین هدایت می‌شود
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const login = (username, password) => {
  return api.post('/auth/login/', { username, password })
}

export const logout = () => {
  return api.post('/auth/logout/')
}

export const checkAuth = () => {
  return api.get('/auth/check/')
}

export const getCoins = () => {
  return api.get('/coins/')
}

export const getSettings = () => {
  return api.get('/settings/')
}

export const updateSettings = (settings) => {
  return api.put('/settings/', settings)
}

export const getMonitoringStatus = () => {
  return api.get('/monitoring/status/')
}

export const startMonitoring = () => {
  return api.post('/monitoring/start/')
}

export const stopMonitoring = () => {
  return api.post('/monitoring/stop/')
}

export const manualUpdate = () => {
  return api.post('/monitoring/update/')
}

export default api

