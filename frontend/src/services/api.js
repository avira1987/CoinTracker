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
  
  // استفاده از hostname و port فعلی صفحه برای ساخت URL
  // این کار باعث می‌شود که از همان hostname و port که صفحه از آن بارگذاری شده استفاده شود
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  const port = window.location.port
  
  // اگر پورت خالی است (پورت پیش‌فرض) یا در حالت development هستیم، از پورت backend استفاده می‌کنیم
  // در حالت production با nginx، از همان پورت صفحه استفاده می‌شود
  let backendPort = port
  if (!port || port === '3000' || port === '6000') {
    // در حالت development، از پورت backend استفاده می‌کنیم
    backendPort = import.meta.env.VITE_BACKEND_PORT || '8000'
  }
  
  // ساخت URL بر اساس hostname و port فعلی
  return `${protocol}//${hostname}${backendPort ? ':' + backendPort : ''}/api`
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

