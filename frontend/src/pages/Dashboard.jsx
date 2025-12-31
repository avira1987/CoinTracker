import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getCoins, getMonitoringStatus, startMonitoring, stopMonitoring, manualUpdate, logout } from '../services/api'
import wsService from '../services/websocket'
import './Dashboard.css'

function Dashboard() {
  const [coins, setCoins] = useState([])
  const [status, setStatus] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    // بارگذاری اولیه
    loadData()

    // اتصال WebSocket
    wsService.connect()

    // تنظیم listeners
    const handleCoinsUpdate = (newCoins) => {
      setCoins(newCoins)
    }

    const handleStatusUpdate = (newStatus) => {
      setStatus(newStatus)
    }

    const handleTimestampUpdate = (timestamp) => {
      setLastUpdate(timestamp)
    }

    const handleError = (error) => {
      console.error('WebSocket error:', error)
    }

    wsService.on('coins', handleCoinsUpdate)
    wsService.on('status', handleStatusUpdate)
    wsService.on('update_timestamp', handleTimestampUpdate)
    wsService.on('error', handleError)

    return () => {
      wsService.off('coins', handleCoinsUpdate)
      wsService.off('status', handleStatusUpdate)
      wsService.off('update_timestamp', handleTimestampUpdate)
      wsService.off('error', handleError)
    }
  }, [])

  const loadData = async () => {
    try {
      const [coinsResponse, statusResponse] = await Promise.all([
        getCoins(),
        getMonitoringStatus()
      ])
      setCoins(coinsResponse.data.results || coinsResponse.data)
      setStatus(statusResponse.data)
      setLoading(false)
    } catch (error) {
      console.error('Error loading data:', error)
      setLoading(false)
    }
  }


  const handleStartMonitoring = async () => {
    setActionLoading(true)
    try {
      await startMonitoring()
      await loadData()
    } catch (error) {
      console.error('Error starting monitoring:', error)
      alert('خطا در شروع پایش')
    } finally {
      setActionLoading(false)
    }
  }

  const handleStopMonitoring = async () => {
    setActionLoading(true)
    try {
      await stopMonitoring()
      await loadData()
    } catch (error) {
      console.error('Error stopping monitoring:', error)
      alert('خطا در توقف پایش')
    } finally {
      setActionLoading(false)
    }
  }

  const handleManualUpdate = async () => {
    setActionLoading(true)
    try {
      await manualUpdate()
      await loadData()
    } catch (error) {
      console.error('Error manual update:', error)
      alert('خطا در به‌روزرسانی')
    } finally {
      setActionLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      window.location.href = '/login'
    } catch (error) {
      console.error('Error logging out:', error)
    }
  }

  const formatNumber = (num) => {
    if (!num) return '0'
    return new Intl.NumberFormat('fa-IR').format(Number(num))
  }

  const formatPrice = (price) => {
    if (!price) return '$0'
    if (price < 0.01) {
      return `$${Number(price).toFixed(8)}`
    }
    return `$${formatNumber(Number(price).toFixed(2))}`
  }

  const formatPercentage = (value) => {
    if (!value) return '0%'
    const num = Number(value)
    const sign = num >= 0 ? '+' : ''
    return `${sign}${num.toFixed(2)}%`
  }

  const getChangeColor = (value) => {
    const num = Number(value)
    if (num > 0) return 'positive'
    if (num < 0) return 'negative'
    return 'neutral'
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date)
  }

  if (loading) {
    return <div className="loading">در حال بارگذاری...</div>
  }

  return (
    <div className="dashboard">
      <header className="header">
        <h1>CoinTracker - رتبه‌بندی ارزهای دیجیتال</h1>
        <nav className="nav-links">
          <Link to="/">داشبورد</Link>
          <Link to="/settings">تنظیمات</Link>
          <button onClick={handleLogout} className="logout-btn">خروج</button>
        </nav>
      </header>

      <div className="content">
        <div className="dashboard-controls">
          <div className="status-info">
            <div className="status-indicator">
              <span className={`status-dot ${status?.is_running ? 'running' : 'stopped'}`}></span>
              <span>{status?.is_running ? 'پایش فعال' : 'پایش غیرفعال'}</span>
            </div>
            {status?.last_update && (
              <div className="last-update">
                آخرین به‌روزرسانی: {formatDate(status.last_update)}
              </div>
            )}
            {lastUpdate && (
              <div className="last-update">
                به‌روزرسانی Real-time: {formatDate(lastUpdate)}
              </div>
            )}
          </div>
          <div className="action-buttons">
            {status?.is_running ? (
              <button 
                onClick={handleStopMonitoring} 
                disabled={actionLoading}
                className="btn btn-stop"
              >
                {actionLoading ? '...' : 'توقف پایش'}
              </button>
            ) : (
              <button 
                onClick={handleStartMonitoring} 
                disabled={actionLoading}
                className="btn btn-start"
              >
                {actionLoading ? '...' : 'شروع پایش'}
              </button>
            )}
            <button 
              onClick={handleManualUpdate} 
              disabled={actionLoading}
              className="btn btn-update"
            >
              {actionLoading ? '...' : 'به‌روزرسانی دستی'}
            </button>
          </div>
        </div>

        <div className="coins-table-container">
          <table className="coins-table">
            <thead>
              <tr>
                <th>رتبه</th>
                <th>نام</th>
                <th>نماد</th>
                <th>قیمت فعلی</th>
                <th>تغییرات 1 ساعت</th>
                <th>تغییرات 24 ساعت</th>
                <th>تغییرات 7 روز</th>
                <th>تغییرات حجم 24h</th>
                <th>حجم بازار</th>
                <th>حجم معاملات 24h</th>
                <th>دلیل رتبه‌بندی</th>
              </tr>
            </thead>
            <tbody>
              {coins.map((coin) => (
                <tr key={coin.id}>
                  <td className="rank-cell">#{coin.rank}</td>
                  <td className="name-cell">{coin.name}</td>
                  <td className="symbol-cell">{coin.symbol}</td>
                  <td>{formatPrice(coin.current_price)}</td>
                  <td className={getChangeColor(coin.price_change_1h)}>
                    {formatPercentage(coin.price_change_1h)}
                  </td>
                  <td className={getChangeColor(coin.price_change_24h)}>
                    {formatPercentage(coin.price_change_24h)}
                  </td>
                  <td className={getChangeColor(coin.price_change_7d)}>
                    {formatPercentage(coin.price_change_7d)}
                  </td>
                  <td className={getChangeColor(coin.volume_change_24h)}>
                    {formatPercentage(coin.volume_change_24h)}
                  </td>
                  <td>${formatNumber(coin.market_cap)}</td>
                  <td>${formatNumber(coin.volume_24h)}</td>
                  <td className="reason-cell">{coin.rank_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

