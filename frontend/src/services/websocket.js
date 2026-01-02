/**
 * سرویس WebSocket برای دریافت به‌روزرسانی‌های Real-time
 */
import ReconnectingWebSocket from 'reconnecting-websocket'

// استفاده از IP عمومی برای WebSocket
const getWebSocketUrl = () => {
  // اگر متغیر محیطی تنظیم شده باشد، از آن استفاده می‌شود
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL
  }
  
  // تشخیص خودکار: اگر در localhost هستیم از localhost استفاده می‌کنیم
  const hostname = window.location.hostname
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'ws://localhost:8000/ws/coins/'
  }
  
  // در غیر این صورت از IP عمومی استفاده می‌کنیم
  // استفاده از ws یا wss بر اساس پروتکل صفحه
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//141.11.0.80:8000/ws/coins/`
}

const WS_URL = getWebSocketUrl()

class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
  }

  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return
    }

    try {
      this.ws = new ReconnectingWebSocket(WS_URL, [], {
        maxReconnectionDelay: 10000,
        minReconnectionDelay: 1000,
        reconnectionDelayGrowFactor: 1.3,
        maxRetries: Infinity,
        connectionTimeout: 4000,
      })

      this.ws.addEventListener('open', () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.emit('connected')
        // درخواست داده اولیه
        this.send({ type: 'get_coins' })
      })

      this.ws.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      })

      this.ws.addEventListener('error', (error) => {
        console.error('WebSocket error:', error)
        this.emit('error', error)
      })

      this.ws.addEventListener('close', () => {
        console.log('WebSocket disconnected')
        this.emit('disconnected')
      })
    } catch (error) {
      console.error('Error connecting WebSocket:', error)
    }
  }

  handleMessage(data) {
    const { type } = data

    switch (type) {
      case 'initial_data':
        this.emit('coins', data.coins)
        this.emit('status', data.status)
        break
      case 'coin_update':
        this.emit('coins', data.coins)
        this.emit('update_timestamp', data.timestamp)
        break
      case 'status_update':
        this.emit('status', data.status)
        break
      case 'error':
        this.emit('error', data.message)
        break
      default:
        console.log('Unknown message type:', type)
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in ${event} callback:`, error)
        }
      })
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners.clear()
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
}

// Singleton instance
const wsService = new WebSocketService()

export default wsService

