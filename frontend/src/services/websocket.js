/**
 * سرویس WebSocket برای دریافت به‌روزرسانی‌های Real-time
 */
import ReconnectingWebSocket from 'reconnecting-websocket'

// تعیین URL WebSocket
const getWebSocketUrl = () => {
  // اگر متغیر محیطی تنظیم شده باشد، از آن استفاده می‌شود
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL
  }
  
  const hostname = window.location.hostname
  const port = window.location.port
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  
  // در حالت development، مستقیماً به backend متصل می‌شویم
  if (port === '3000' || port === '6000' || port === '5173') {
    return `ws://localhost:8000/ws/coins/`
  }
  
  // در حالت production
  let wsPort = port
  if (!port || port === '' || port === '80' || port === '443') {
    wsPort = ''
  }
  
  return `${protocol}//${hostname}${wsPort ? ':' + wsPort : ''}/ws/coins/`
}

class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.isConnecting = false
  }

  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('✅ WebSocket already connected')
      return
    }

    if (this.isConnecting) {
      console.log('⏳ WebSocket connection in progress...')
      return
    }

    const wsUrl = getWebSocketUrl()
    console.log('🔧 Connecting to WebSocket:', wsUrl)
    this.isConnecting = true

    try {
      this.ws = new ReconnectingWebSocket(wsUrl, [], {
        maxReconnectionDelay: 10000,
        minReconnectionDelay: 1000,
        reconnectionDelayGrowFactor: 1.3,
        maxRetries: Infinity,
        connectionTimeout: 4000,
      })

      this.ws.addEventListener('open', () => {
        console.log('✅ WebSocket connected')
        this.isConnecting = false
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
          console.error('❌ Error parsing WebSocket message:', error)
        }
      })

      this.ws.addEventListener('error', (error) => {
        console.error('❌ WebSocket error:', error)
        this.isConnecting = false
        this.emit('error', error)
      })

      this.ws.addEventListener('close', () => {
        console.log('⚠️ WebSocket disconnected')
        this.isConnecting = false
        this.emit('disconnected')
      })
    } catch (error) {
      console.error('❌ Error connecting WebSocket:', error)
      this.isConnecting = false
      this.emit('error', error)
    }
  }

  handleMessage(data) {
    const { type } = data

    switch (type) {
      case 'initial_data':
        console.log('📊 WebSocket: initial data received')
        this.emit('coins', data.coins)
        this.emit('status', data.status)
        break
      case 'coin_update':
        console.log('📊 WebSocket: coin update received')
        this.emit('coins', data.coins)
        if (data.timestamp) {
          this.emit('update_timestamp', data.timestamp)
        }
        break
      case 'status_update':
        console.log('📊 WebSocket: status update received')
        this.emit('status', data.status)
        break
      case 'error':
        console.error('❌ WebSocket error message:', data.message)
        this.emit('error', data.message)
        break
      default:
        console.log('⚠️ Unknown WebSocket message type:', type)
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
          console.error(`❌ Error in ${event} callback:`, error)
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
    this.isConnecting = false
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('⚠️ WebSocket is not open, cannot send message')
    }
  }
}

// Singleton instance
const wsService = new WebSocketService()

export default wsService
