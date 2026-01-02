import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getCoins, getMonitoringStatus, startMonitoring, stopMonitoring, manualUpdate } from '../services/api'
import wsService from '../services/websocket'
import './Dashboard.css'

function Dashboard() {
  const [coins, setCoins] = useState([])
  const [status, setStatus] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [isDescriptionOpen, setIsDescriptionOpen] = useState(false)

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
          <Link to="/tutorial">آموزش</Link>
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

        <div className="monitoring-description">
          <button 
            className="description-toggle"
            onClick={() => setIsDescriptionOpen(!isDescriptionOpen)}
            aria-expanded={isDescriptionOpen}
          >
            <span>نحوه کار سیستم پایش</span>
            <span className={`toggle-icon ${isDescriptionOpen ? 'open' : ''}`}>▼</span>
          </button>
          <div className={`description-content ${isDescriptionOpen ? 'open' : 'closed'}`}>
            <div className="description-section">
              <h3>📊 جمع‌آوری داده‌ها</h3>
              <p>
                سیستم به صورت خودکار و در بازه‌های زمانی مشخص (قابل تنظیم در بخش تنظیمات) 
                داده‌های ارزهای دیجیتال را از API سرویس CoinGecko دریافت می‌کند. این داده‌ها شامل 
                قیمت فعلی، تغییرات قیمت (1 ساعت، 24 ساعت، 7 روز)، حجم معاملات، حجم بازار و سایر 
                اطلاعات مهم می‌باشد.
              </p>
            </div>
            <div className="description-section">
              <h3>🔢 محاسبه رتبه‌بندی</h3>
              <p>
                پس از دریافت داده‌ها، سیستم با استفاده از یک فرمول وزنی هوشمند، رتبه هر ارز دیجیتال 
                را محاسبه می‌کند. این فرمول بر اساس معیارهای زیر عمل می‌کند:
              </p>
              <ul>
                <li><strong>تغییرات قیمت (40%)</strong>: روند تغییرات قیمت در 24 ساعت گذشته</li>
                <li><strong>تغییرات حجم (30%)</strong>: میزان تغییر حجم معاملات در 24 ساعت</li>
                <li><strong>پایداری (20%)</strong>: محاسبه شده بر اساس واریانس قیمت، ثبات روند و ریسک برگشت</li>
                <li><strong>حجم بازار (10%)</strong>: ارزش کل بازار هر ارز دیجیتال</li>
              </ul>
              <p>
                بر اساس این محاسبات، هر کوین یک نمره کلی دریافت می‌کند و سپس بر اساس این نمره 
                رتبه‌بندی می‌شود. همچنین دلیل اصلی رتبه‌بندی هر کوین در ستون «دلیل رتبه‌بندی» نمایش داده می‌شود.
              </p>
            </div>
            <div className="description-section">
              <h3>🔄 به‌روزرسانی Real-time</h3>
              <p>
                سیستم از فناوری WebSocket برای ارسال به‌روزرسانی‌های لحظه‌ای به مرورگر شما استفاده می‌کند. 
                این به معنای آن است که بدون نیاز به رفرش کردن صفحه، داده‌ها به صورت خودکار به‌روز می‌شوند 
                و شما همیشه آخرین اطلاعات را مشاهده می‌کنید.
              </p>
            </div>
            <div className="description-section">
              <h3>⚙️ کنترل پایش</h3>
              <p>
                شما می‌توانید سیستم پایش را با استفاده از دکمه «شروع پایش» فعال کنید تا به صورت خودکار 
                و منظم داده‌ها را به‌روزرسانی کند. همچنین می‌توانید از دکمه «توقف پایش» برای متوقف کردن 
                به‌روزرسانی خودکار استفاده کنید. دکمه «به‌روزرسانی دستی» امکان به‌روزرسانی فوری داده‌ها 
                بدون نیاز به انتظار برای بازه زمانی بعدی را فراهم می‌کند.
              </p>
            </div>
            <div className="description-section">
              <h3>📈 نمایش اطلاعات</h3>
              <p>
                تمام اطلاعات جمع‌آوری شده در جدول زیر نمایش داده می‌شود. تغییرات مثبت با رنگ سبز و 
                تغییرات منفی با رنگ قرمز مشخص شده‌اند. این به شما کمک می‌کند تا به سرعت روند بازار را 
                درک کنید و تصمیمات آگاهانه‌تری بگیرید.
              </p>
            </div>
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
                <th>1h</th>
                <th>24h</th>
                <th>7d</th>
                <th>حجم 24h</th>
                <th>بازار</th>
                <th>معاملات 24h</th>
              </tr>
            </thead>
            <tbody>
              {coins.map((coin) => (
                <tr key={coin.id}>
                  <td className="rank-cell">#{coin.rank}</td>
                  <td className="name-cell">
                    <div className="name-with-reason">
                      <span className="coin-name">{coin.name}</span>
                      {coin.rank_reason && (
                        <span className="rank-reason-badge">
                          {coin.rank_reason.split(' | ')[0]}
                        </span>
                      )}
                    </div>
                  </td>
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

