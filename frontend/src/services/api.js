/**
 * سرویس API برای ارتباط با Backend
 * استفاده از fetch به جای axios برای سادگی و قابلیت اطمینان بیشتر
 */

// تعیین URL پایه API
const getApiBaseUrl = () => {
  // اگر متغیر محیطی تنظیم شده باشد، از آن استفاده می‌شود
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // در حالت development، مستقیماً به backend متصل می‌شویم
  // چون Vite proxy ممکن است کار نکند
  const port = window.location.port
  const isDevelopment = port === '3000' || port === '6000' || port === '5173' || !port
  
  if (isDevelopment) {
    // مستقیماً به backend متصل می‌شویم
    return 'http://localhost:8000/api'
  }
  
  // در حالت production
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  return `${protocol}//${hostname}${port ? ':' + port : ''}/api`
}

const API_BASE_URL = getApiBaseUrl()
console.log('🔧 API Base URL:', API_BASE_URL)

// تابع کمکی برای درخواست‌های API
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    ...options,
  }

  // ترکیب headers
  if (options.headers) {
    defaultOptions.headers = { ...defaultOptions.headers, ...options.headers }
  }

  // تعیین timeout بر اساس endpoint
  // برای عملیات‌های سنگین مثل به‌روزرسانی، timeout بیشتری در نظر می‌گیریم
  let timeout = 15000 // 15 ثانیه پیش‌فرض
  if (endpoint.includes('/monitoring/update/') || 
      endpoint.includes('/standing/update/') ||
      (endpoint.includes('/standing/') && endpoint.includes('limit=10000'))) {
    timeout = 180000 // 3 دقیقه برای عملیات‌های سنگین
    console.log(`⏱️ استفاده از timeout طولانی (${timeout/1000} ثانیه) برای: ${endpoint}`)
  } else if (endpoint.includes('/monitoring/') || 
             endpoint.includes('/standing/')) {
    timeout = 60000 // 1 دقیقه برای سایر عملیات standing
    console.log(`⏱️ استفاده از timeout متوسط (${timeout/1000} ثانیه) برای: ${endpoint}`)
  }

  try {
    console.log(`📡 درخواست API: ${endpoint} (timeout: ${timeout/1000} ثانیه)`)
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    const response = await fetch(url, {
      ...defaultOptions,
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      let errorMessage = `خطا: ${response.status} ${response.statusText}`
      try {
        const errorData = await response.json()
        if (errorData.message) {
          errorMessage = errorData.message
        } else if (errorData.error) {
          errorMessage = errorData.error
        }
      } catch (e) {
        // اگر JSON parse نشد، از پیام پیش‌فرض استفاده می‌کنیم
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()
    return { data, status: response.status }
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error(`❌ Timeout برای ${endpoint} بعد از ${timeout/1000} ثانیه`)
      throw new Error(`زمان انتظار به پایان رسید (${timeout/1000} ثانیه). این عملیات ممکن است زمان بیشتری نیاز داشته باشد. لطفاً دوباره تلاش کنید.`)
    }
    if (error.message) {
      console.error(`❌ خطا در ${endpoint}:`, error.message)
      throw error
    }
    console.error(`❌ خطای نامشخص در ${endpoint}:`, error)
    throw new Error('خطا در ارتباط با سرور. لطفاً اتصال اینترنت و وضعیت سرور را بررسی کنید.')
  }
}

// توابع API
export const login = (username, password) => {
  return apiRequest('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export const logout = () => {
  return apiRequest('/auth/logout/', {
    method: 'POST',
  })
}

export const checkAuth = () => {
  return apiRequest('/auth/check/')
}

export const getCoins = async () => {
  const response = await apiRequest('/coins/')
  // REST Framework ممکن است results را در data.results برگرداند
  if (response.data.results) {
    return { data: { results: response.data.results } }
  }
  return { data: response.data }
}

export const getSettings = () => {
  return apiRequest('/settings/')
}

export const updateSettings = (settings) => {
  return apiRequest('/settings/', {
    method: 'PUT',
    body: JSON.stringify(settings),
  })
}

export const getMonitoringStatus = () => {
  return apiRequest('/monitoring/status/')
}

export const startMonitoring = () => {
  return apiRequest('/monitoring/start/', {
    method: 'POST',
  })
}

export const stopMonitoring = () => {
  return apiRequest('/monitoring/stop/', {
    method: 'POST',
  })
}

export const manualUpdate = () => {
  return apiRequest('/monitoring/update/', {
    method: 'POST',
  })
}

// تابع برای دریافت داده‌های standing
export const getStanding = async (limit = 10000, offset = 0, symbol = null) => {
  const params = new URLSearchParams()
  if (limit) params.append('limit', limit)
  if (offset) params.append('offset', offset)
  if (symbol) params.append('symbol', symbol)
  
  const endpoint = `/standing/?${params.toString()}`
  console.log('📡 Fetching standing from:', endpoint)
  
  try {
    const response = await apiRequest(endpoint)
    console.log('✅ Standing data received:', {
      indicatorsCount: response.data?.indicators?.length || 0,
      total: response.data?.total || 0,
    })
    return response
  } catch (error) {
    console.error('❌ Error in getStanding:', error)
    throw error
  }
}

// تابع برای به‌روزرسانی دستی داده‌های standing
export const updateStanding = () => {
  return apiRequest('/standing/update/', {
    method: 'POST',
  })
}

// تابع برای دریافت مستقیم داده‌های سوشال از API خارجی
export const fetchSocialData = async (limit = 10000, offset = 0, symbol = null) => {
  const params = new URLSearchParams()
  if (limit) params.append('limit', limit)
  if (offset) params.append('offset', offset)
  if (symbol) params.append('symbol', symbol)
  
  const endpoint = `/social/fetch/?${params.toString()}`
  console.log('📡 Fetching social data from external API:', endpoint)
  
  try {
    const response = await apiRequest(endpoint)
    console.log('✅ Social data received:', {
      indicatorsCount: response.data?.indicators?.length || 0,
      total: response.data?.total || 0,
      source: response.data?.source || 'unknown',
    })
    return response
  } catch (error) {
    console.error('❌ Error in fetchSocialData:', error)
    throw error
  }
}

export default { apiRequest }
