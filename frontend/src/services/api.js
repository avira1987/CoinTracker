/**
 * سرویس API برای ارتباط با Backend
 */
import axios from 'axios'

// استفاده از IP عمومی برای API
const getApiBaseUrl = () => {
  // اگر متغیر محیطی تنظیم شده باشد، از آن استفاده می‌شود
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // تشخیص خودکار: اگر در localhost هستیم از localhost استفاده می‌کنیم
  const hostname = window.location.hostname
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000/api'
  }
  
  // در غیر این صورت از IP عمومی استفاده می‌کنیم
  return 'http://141.11.0.80:8000/api'
}

const API_BASE_URL = getApiBaseUrl()

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
    // صفحه لاگین غیرفعال شده است - دیگر redirect به لاگین انجام نمی‌شود
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

