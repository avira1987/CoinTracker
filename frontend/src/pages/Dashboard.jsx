import React, { useState, useEffect, useRef, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { getCoins, getMonitoringStatus, startMonitoring, stopMonitoring, manualUpdate, getStanding, updateStanding } from '../services/api'
import wsService from '../services/websocket'
import './Dashboard.css'

function Dashboard() {
  const [coins, setCoins] = useState([])
  const [status, setStatus] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [isDescriptionOpen, setIsDescriptionOpen] = useState(false)
  const [standingData, setStandingData] = useState({})
  const [standingSource, setStandingSource] = useState(null)
  const [error, setError] = useState(null)
  const [timeUntilUpdate, setTimeUntilUpdate] = useState(null)
  const retryCountRef = useRef(0)
  const maxRetries = 3

  // بارگذاری اولیه داده‌ها
  useEffect(() => {
    loadInitialData()
    
    // اتصال WebSocket
    wsService.connect()
    
    // تنظیم listeners برای WebSocket
    const handleCoinsUpdate = (newCoins) => {
      console.log('📊 WebSocket: کوین‌ها به‌روزرسانی شدند', newCoins?.length)
      if (Array.isArray(newCoins)) {
        setCoins(newCoins)
      }
    }

    const handleStatusUpdate = (newStatus) => {
      console.log('📊 WebSocket: وضعیت به‌روزرسانی شد', newStatus)
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

  // محاسبه زمان باقی‌مانده تا بروزرسانی بعدی
  useEffect(() => {
    const calculateTimeUntilUpdate = () => {
      if (!status?.next_update || !status?.is_running) {
        setTimeUntilUpdate(null)
        return
      }

      const now = new Date()
      const nextUpdate = new Date(status.next_update)
      const diff = nextUpdate - now

      if (diff <= 0) {
        setTimeUntilUpdate('هم اکنون')
        return
      }

      const minutes = Math.floor(diff / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)

      if (minutes > 0) {
        setTimeUntilUpdate(`${minutes} دقیقه و ${seconds} ثانیه`)
      } else {
        setTimeUntilUpdate(`${seconds} ثانیه`)
      }
    }

    calculateTimeUntilUpdate()
    const interval = setInterval(calculateTimeUntilUpdate, 1000)

    return () => clearInterval(interval)
  }, [status])

  // بارگذاری داده‌های standing
  useEffect(() => {
    loadStandingData()
  }, [])

  // سورت کردن coins بر اساس سوشال رنک (standing) از بزرگ به کوچک
  const sortedCoins = useMemo(() => {
    if (coins.length === 0) return []
    
    return [...coins].sort((a, b) => {
      const symbolA = a.symbol?.toUpperCase()
      const symbolB = b.symbol?.toUpperCase()
      const standingA = standingData[symbolA]
      const standingB = standingData[symbolB]
      
      // اگر هر دو standing دارند، بر اساس standing سورت کن (بزرگترین به کوچکترین)
      if (standingA !== undefined && standingA !== null && standingB !== undefined && standingB !== null) {
        return standingB - standingA
      }
      // اگر فقط یکی standing دارد، آن را اول بگذار
      if (standingA !== undefined && standingA !== null) return -1
      if (standingB !== undefined && standingB !== null) return 1
      // اگر هیچکدام standing ندارند، بر اساس rank_score سورت کن
      return (b.rank_score || 0) - (a.rank_score || 0)
    })
  }, [coins, standingData])

  const loadInitialData = async () => {
    try {
      setError(null)
      setLoading(true)
      retryCountRef.current = 0

      console.log('🔄 شروع بارگذاری داده‌ها...')
      
      // بارگذاری همزمان کوین‌ها و وضعیت
      const [coinsResponse, statusResponse] = await Promise.all([
        getCoins(),
        getMonitoringStatus()
      ])

      console.log('✅ داده‌ها با موفقیت بارگذاری شدند')
      console.log('   کوین‌ها:', coinsResponse.data?.results?.length || coinsResponse.data?.length || 0)
      console.log('   وضعیت:', statusResponse.data)

      // تنظیم state
      const coinsList = coinsResponse.data?.results || coinsResponse.data || []
      setCoins(Array.isArray(coinsList) ? coinsList : [])
      setStatus(statusResponse.data)
      setLoading(false)
    } catch (error) {
      console.error('❌ خطا در بارگذاری داده‌ها:', error)
      handleLoadError(error)
    }
  }

  const loadStandingData = async () => {
    try {
      console.log('🔄 بارگذاری داده‌های standing...')
      const standingResponse = await getStanding(10000, 0, null)
      
      if (!standingResponse?.data) {
        console.warn('⚠️ پاسخ standing نامعتبر است')
        return
      }

      // بررسی خطا در پاسخ
      if (standingResponse.data.error) {
        console.warn('⚠️ خطا در API standing:', standingResponse.data.error)
        return
      }

      const indicators = standingResponse.data.indicators || []
      const sourceInfo = standingResponse.data.source || null
      console.log('📊 تعداد indicators:', indicators.length)
      console.log('📊 اطلاعات منبع:', sourceInfo)

      if (indicators.length === 0) {
        console.warn('⚠️ هیچ indicator دریافت نشد - ممکن است standing هنوز به‌روزرسانی نشده باشد')
        console.log('💡 پیشنهاد: دکمه "به‌روزرسانی دستی" را بزنید تا standing data دریافت شود')
        return
      }

      // ساخت Map از symbol به standing
      const standingMap = {}
      indicators.forEach(indicator => {
        const symbol = indicator.symbol?.toUpperCase()
        const standing = indicator.standing
        if (symbol && standing !== undefined && standing !== null) {
          standingMap[symbol] = standing
        }
      })

      console.log('✅ Standing map ایجاد شد:', Object.keys(standingMap).length, 'ورودی')
      if (Object.keys(standingMap).length > 0) {
        console.log('📋 نمونه standing data:', Object.entries(standingMap).slice(0, 5))
      }
      setStandingData(standingMap)
      setStandingSource(sourceInfo)
    } catch (error) {
      console.error('❌ خطا در بارگذاری standing:', error)
      console.log('💡 پیشنهاد: مطمئن شوید که standing data از API خارجی دریافت شده است')
      // خطا را نادیده می‌گیریم تا صفحه کار کند
    }
  }

  const handleLoadError = (error) => {
    const errorMessage = error.message || 'خطا در بارگذاری داده‌ها'
    
    if (retryCountRef.current < maxRetries) {
      retryCountRef.current += 1
      console.log(`🔄 تلاش مجدد ${retryCountRef.current}/${maxRetries}...`)
      setTimeout(() => {
        loadInitialData()
      }, 2000 * retryCountRef.current) // تاخیر افزایشی
    } else {
      setError(errorMessage)
      setLoading(false)
      retryCountRef.current = 0
    }
  }

  const handleStartMonitoring = async () => {
    setActionLoading(true)
    setError(null)
    try {
      const response = await startMonitoring()
      if (response.data && !response.data.success) {
        throw new Error(response.data.message || 'خطا در شروع پایش')
      }
      await loadInitialData()
    } catch (error) {
      console.error('Error starting monitoring:', error)
      setError(error.message || 'خطا در شروع پایش')
    } finally {
      setActionLoading(false)
    }
  }

  const handleStopMonitoring = async () => {
    setActionLoading(true)
    setError(null)
    try {
      const response = await stopMonitoring()
      if (response.data && !response.data.success) {
        throw new Error(response.data.message || 'خطا در توقف پایش')
      }
      await loadInitialData()
    } catch (error) {
      console.error('Error stopping monitoring:', error)
      setError(error.message || 'خطا در توقف پایش')
    } finally {
      setActionLoading(false)
    }
  }

  const handleManualUpdate = async () => {
    setActionLoading(true)
    setError(null)
    try {
      console.log('🔄 شروع به‌روزرسانی دستی...')
      
      // به‌روزرسانی داده‌های اصلی
      const response = await manualUpdate()
      if (response.data && !response.data.success) {
        throw new Error(response.data.message || 'خطا در به‌روزرسانی')
      }
      console.log('✅ به‌روزرسانی دستی موفق بود')
      
      // به‌روزرسانی standing از API خارجی
      try {
        console.log('🔄 به‌روزرسانی داده‌های standing...')
        const standingUpdateResponse = await updateStanding()
        if (standingUpdateResponse.data && standingUpdateResponse.data.success) {
          console.log('✅ Standing data updated successfully')
        } else {
          console.warn('⚠️ Standing update returned:', standingUpdateResponse.data)
        }
      } catch (standingError) {
        console.warn('⚠️ خطا در به‌روزرسانی standing (ادامه می‌دهیم):', standingError)
        // خطا را نادیده می‌گیریم تا به‌روزرسانی اصلی ادامه یابد
      }
      
      // بارگذاری مجدد داده‌ها
      await loadInitialData()
      
      // بارگذاری standing با تاخیر کوتاه برای اطمینان از ذخیره شدن در دیتابیس
      setTimeout(async () => {
        console.log('🔄 بارگذاری مجدد standing بعد از به‌روزرسانی...')
        await loadStandingData()
      }, 2000)
    } catch (error) {
      console.error('Error manual update:', error)
      setError(error.message || 'خطا در به‌روزرسانی')
    } finally {
      setActionLoading(false)
    }
  }

  // توابع فرمت
  const formatNumber = (num) => {
    if (!num && num !== 0) return '0'
    return new Intl.NumberFormat('fa-IR').format(Number(num))
  }

  const formatPrice = (price) => {
    if (!price && price !== 0) return '$0'
    if (price < 0.01) {
      return `$${Number(price).toFixed(8)}`
    }
    return `$${formatNumber(Number(price).toFixed(2))}`
  }

  const formatPercentage = (value) => {
    if (!value && value !== 0) return '0%'
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
    try {
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('fa-IR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).format(date)
    } catch (e) {
      return dateString
    }
  }

  // نمایش loading
  if (loading) {
    return (
      <div className="loading">
        <div>در حال بارگذاری...</div>
        {error && (
          <div style={{ marginTop: '20px', color: '#ff4444', fontSize: '14px' }}>
            {error}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="dashboard">
      <header className="header">
        <h1>CoinTracker - رتبه‌بندی ارزهای دیجیتال</h1>
        <nav className="nav-links">
          <Link to="/">داشبورد</Link>
          <Link to="/social-data">📊 داده‌های سوشال</Link>
          <Link to="/settings">تنظیمات</Link>
          <Link to="/tutorial">آموزش</Link>
          <Link to="/documentation">📚 مستندات</Link>
        </nav>
      </header>

      {error && (
        <div className="error-banner" style={{
          background: '#ffebee',
          color: '#c62828',
          padding: '15px',
          margin: '20px',
          borderRadius: '4px',
          border: '1px solid #ef5350'
        }}>
          <strong>خطا:</strong> {error}
          <button 
            onClick={() => {
              setError(null)
              setLoading(true)
              loadInitialData()
            }}
            style={{
              marginLeft: '15px',
              padding: '5px 15px',
              background: '#c62828',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            تلاش مجدد
          </button>
        </div>
      )}

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
            {status?.next_update && status?.is_running && (
              <div className="next-update" style={{ 
                fontSize: '14px', 
                color: '#1976d2',
                fontWeight: 'bold',
                marginTop: '5px'
              }}>
                بروزرسانی بعدی: {timeUntilUpdate ? `در ${timeUntilUpdate}` : formatDate(status.next_update)}
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
            <span>📚 راهنمای کامل سیستم - چه کاری انجام می‌دهد و چه کاری نمی‌کند</span>
            <span className={`toggle-icon ${isDescriptionOpen ? 'open' : ''}`}>▼</span>
          </button>
          <div className={`description-content ${isDescriptionOpen ? 'open' : 'closed'}`}>
            <div className="description-section">
              <h3>✅ چه کاری انجام می‌دهد:</h3>
              <ul style={{ textAlign: 'right', lineHeight: '2', paddingRight: '20px' }}>
                <li><strong>📊 رتبه‌بندی هوشمند:</strong> ارزهای دیجیتال را بر اساس فرمول وزن‌دار رتبه‌بندی می‌کند</li>
                <li><strong>🔄 به‌روزرسانی خودکار:</strong> داده‌ها را به صورت خودکار در بازه‌های زمانی مشخص (پیش‌فرض: هر 60 ثانیه) به‌روزرسانی می‌کند</li>
                <li><strong>📈 جمع‌آوری داده:</strong> اطلاعات قیمت، حجم معاملات، تغییرات 1h، 24h و 7d را از CoinGecko API دریافت می‌کند</li>
                <li><strong>🌟 سوشال رنک:</strong> داده‌های Social Standing را از APIهای خارجی دریافت و نمایش می‌دهد (هر 1 ساعت به‌روزرسانی)</li>
                <li><strong>⚡ Real-time Updates:</strong> با استفاده از WebSocket، به‌روزرسانی‌های لحظه‌ای را به مرورگر ارسال می‌کند</li>
                <li><strong>💾 ذخیره تاریخچه:</strong> تاریخچه قیمت‌ها را برای محاسبه ثبات (Stability) ذخیره می‌کند</li>
                <li><strong>🎛️ قابل تنظیم:</strong> وزن‌های رتبه‌بندی، تعداد کوین‌ها و بازه به‌روزرسانی قابل تنظیم است</li>
              </ul>
            </div>
            <div className="description-section">
              <h3>❌ چه کاری انجام نمی‌دهد:</h3>
              <ul style={{ textAlign: 'right', lineHeight: '2', paddingRight: '20px' }}>
                <li><strong>⚠️ پیش‌بینی قیمت:</strong> این سیستم پیش‌بینی قیمت آینده ارزها را انجام نمی‌دهد</li>
                <li><strong>💰 مشاوره سرمایه‌گذاری:</strong> این یک ابزار تحلیلی است و مشاوره سرمایه‌گذاری ارائه نمی‌دهد</li>
                <li><strong>📱 اپلیکیشن موبایل:</strong> فعلاً فقط نسخه وب دارد</li>
                <li><strong>🔔 اعلان‌های پیشرفته:</strong> سیستم اعلان برای تغییرات قیمت ندارد</li>
                <li><strong>📊 نمودارهای پیشرفته:</strong> نمودارهای تحلیل تکنیکال ارائه نمی‌دهد</li>
                <li><strong>🌐 پشتیبانی از چند صرافی:</strong> فقط از CoinGecko API استفاده می‌کند</li>
                <li><strong>💵 معامله خودکار:</strong> هیچ معامله یا تراکنش خودکاری انجام نمی‌دهد</li>
              </ul>
            </div>
            <div className="description-section" style={{ 
              background: '#e3f2fd', 
              padding: '15px', 
              borderRadius: '8px', 
              marginTop: '15px',
              border: '2px solid #2196f3'
            }}>
              <h3>⏰ زمان بروزرسانی بعدی:</h3>
              {status?.is_running ? (
                <div>
                  {timeUntilUpdate ? (
                    <p style={{ fontSize: '18px', fontWeight: 'bold', color: '#1976d2', marginTop: '10px' }}>
                      تا بروزرسانی بعدی: <span style={{ color: '#d32f2f' }}>{timeUntilUpdate}</span>
                    </p>
                  ) : status?.next_update ? (
                    <p style={{ fontSize: '16px', marginTop: '10px' }}>
                      بروزرسانی بعدی: {formatDate(status.next_update)}
                    </p>
                  ) : (
                    <p style={{ fontSize: '16px', marginTop: '10px' }}>
                      در حال محاسبه...
                    </p>
                  )}
                  {status?.last_update && (
                    <p style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                      آخرین بروزرسانی: {formatDate(status.last_update)}
                    </p>
                  )}
                </div>
              ) : (
                <p style={{ fontSize: '16px', color: '#d32f2f', fontWeight: 'bold' }}>
                  ⚠️ پایش غیرفعال است - برای فعال‌سازی دکمه "شروع پایش" را بزنید
                </p>
              )}
            </div>
            <div className="description-section">
              <h3>🔧 نحوه کار سیستم:</h3>
              <ol style={{ textAlign: 'right', lineHeight: '2', paddingRight: '20px' }}>
                <li><strong>جمع‌آوری داده:</strong> سیستم به صورت خودکار داده‌های ارزهای دیجیتال را از API دریافت می‌کند</li>
                <li><strong>محاسبه رتبه:</strong> با استفاده از فرمول وزن‌دار، رتبه هر ارز محاسبه می‌شود</li>
                <li><strong>ذخیره در دیتابیس:</strong> اطلاعات در دیتابیس SQLite ذخیره می‌شود</li>
                <li><strong>ارسال به کاربر:</strong> از طریق WebSocket، به‌روزرسانی‌ها به تمام کاربران ارسال می‌شود</li>
              </ol>
            </div>
          </div>
        </div>

        <div className="coins-table-container">
          {sortedCoins.length === 0 ? (
            <div style={{ 
              padding: '60px 40px', 
              textAlign: 'center', 
              background: '#f5f5f5',
              borderRadius: '8px',
              margin: '20px'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '20px' }}>📊</div>
              <h3 style={{ color: '#333', marginBottom: '15px' }}>دیتابیس خالی است</h3>
              <p style={{ color: '#666', marginBottom: '30px', lineHeight: '1.6' }}>
                برای شروع، باید داده‌ها را از CoinGecko API دریافت کنید.
                <br />
                لطفاً دکمه "به‌روزرسانی دستی" را در بالا بزنید یا "شروع پایش" را فعال کنید.
              </p>
              <button 
                onClick={handleManualUpdate}
                disabled={actionLoading}
                className="btn btn-update"
                style={{
                  padding: '12px 30px',
                  fontSize: '16px',
                  fontWeight: 'bold'
                }}
              >
                {actionLoading ? 'در حال به‌روزرسانی...' : '🔄 به‌روزرسانی دستی داده‌ها'}
              </button>
              {error && (
                <div style={{ 
                  marginTop: '20px', 
                  padding: '15px', 
                  background: '#ffebee', 
                  color: '#c62828', 
                  borderRadius: '4px',
                  fontSize: '14px'
                }}>
                  <strong>خطا:</strong> {error}
                </div>
              )}
            </div>
          ) : (
            <table className="coins-table">
              <thead>
                <tr>
                  <th>رتبه</th>
                  <th>نام</th>
                  <th>سوشال رنک</th>
                  <th>نماد</th>
                  <th>قیمت فعلی</th>
                  <th>1h</th>
                  <th>24h</th>
                  <th>7d</th>
                  <th>حجم 24h</th>
                  <th>بازار</th>
                  <th>معاملات 24h</th>
                  <th>منبع و زمان</th>
                </tr>
              </thead>
              <tbody>
                {sortedCoins.map((coin) => (
                  <tr key={coin.id || coin.coin_id}>
                    <td className="rank-cell">#{coin.rank || '-'}</td>
                    <td className="name-cell">
                      <div className="name-with-reason">
                        <span className="coin-name">{coin.name || '-'}</span>
                        {coin.rank_reason && (
                          <span className="rank-reason-badge">
                            {coin.rank_reason.split(' | ')[0]}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="social-rank-cell">
                      {(() => {
                        const symbol = coin.symbol?.toUpperCase()
                        if (!symbol) return '-'
                        const standing = standingData[symbol]
                        if (standing !== undefined && standing !== null) {
                          return formatNumber(standing)
                        }
                        return '-'
                      })()}
                    </td>
                    <td className="symbol-cell">{coin.symbol || '-'}</td>
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
                    <td className="source-cell" style={{ fontSize: '11px', color: '#666' }}>
                      {(() => {
                        if (!standingSource) return '-'
                        const symbol = coin.symbol?.toUpperCase()
                        const hasStanding = symbol && standingData[symbol] !== undefined && standingData[symbol] !== null
                        if (!hasStanding) return '-'
                        
                        const apiName = standingSource.api_name || 'API اول'
                        const lastFetch = standingSource.last_fetch
                        const fromCache = standingSource.from_cache
                        
                        if (lastFetch) {
                          try {
                            const date = new Date(lastFetch)
                            const formattedDate = new Intl.DateTimeFormat('fa-IR', {
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit'
                            }).format(date)
                            return (
                              <div>
                                <div>{apiName}</div>
                                <div style={{ fontSize: '10px', marginTop: '2px', opacity: 0.8 }}>
                                  {fromCache ? 'از cache' : 'مستقیم'} - {formattedDate}
                                </div>
                              </div>
                            )
                          } catch (e) {
                            return apiName
                          }
                        }
                        return apiName
                      })()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
