import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { fetchSocialData } from '../services/api'
import './SocialData.css'

function SocialData() {
  const [socialData, setSocialData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sourceInfo, setSourceInfo] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: 'standing', direction: 'desc' })
  const [refreshing, setRefreshing] = useState(false)
  const retryCountRef = useRef(0)
  const maxRetries = 3

  // بارگذاری اولیه داده‌ها
  useEffect(() => {
    loadSocialData()
  }, [])

  const loadSocialData = async (forceRefresh = false) => {
    try {
      setError(null)
      if (!forceRefresh) {
        setLoading(true)
      } else {
        setRefreshing(true)
      }
      retryCountRef.current = 0

      console.log('🔄 شروع بارگذاری داده‌های سوشال...')
      
      const response = await fetchSocialData(10000, 0, null)

      console.log('✅ داده‌های سوشال با موفقیت بارگذاری شدند')
      console.log('   تعداد indicators:', response.data?.indicators?.length || 0)
      console.log('   منابع:', response.data?.sources || [])

      const indicators = response.data?.indicators || []
      setSocialData(indicators)
      
      // ذخیره اطلاعات منبع
      setSourceInfo({
        sources: response.data?.sources || [],
        api1_count: response.data?.api1_count || 0,
        api2_count: response.data?.api2_count || 0,
        merged_count: response.data?.merged_count || 0,
        timestamp: response.data?.timestamp,
        cache_info: response.data?.cache_info || {}
      })
      
      setLoading(false)
      setRefreshing(false)
    } catch (error) {
      console.error('❌ خطا در بارگذاری داده‌های سوشال:', error)
      handleLoadError(error)
    }
  }

  const handleLoadError = (error) => {
    const errorMessage = error.message || 'خطا در بارگذاری داده‌های سوشال'
    
    if (retryCountRef.current < maxRetries) {
      retryCountRef.current += 1
      console.log(`🔄 تلاش مجدد ${retryCountRef.current}/${maxRetries}...`)
      setTimeout(() => {
        loadSocialData()
      }, 2000 * retryCountRef.current)
    } else {
      setError(errorMessage)
      setLoading(false)
      setRefreshing(false)
      retryCountRef.current = 0
    }
  }

  const handleRefresh = () => {
    loadSocialData(true)
  }

  // سورت کردن داده‌ها
  const sortedData = React.useMemo(() => {
    let sortableData = [...socialData]
    
    // فیلتر بر اساس جستجو
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      sortableData = sortableData.filter(item => 
        item.symbol?.toLowerCase().includes(term) ||
        item.name?.toLowerCase().includes(term)
      )
    }
    
    // سورت
    if (sortConfig.key) {
      sortableData.sort((a, b) => {
        let aValue = a[sortConfig.key]
        let bValue = b[sortConfig.key]
        
        // تبدیل به عدد اگر ممکن باشد
        if (typeof aValue === 'string' && !isNaN(aValue)) aValue = Number(aValue)
        if (typeof bValue === 'string' && !isNaN(bValue)) bValue = Number(bValue)
        
        // مقادیر null را به آخر ببر
        if (aValue === null || aValue === undefined) return 1
        if (bValue === null || bValue === undefined) return -1
        
        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1
        }
        return 0
      })
    }
    
    return sortableData
  }, [socialData, searchTerm, sortConfig])

  const requestSort = (key) => {
    let direction = 'desc'
    if (sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc'
    }
    setSortConfig({ key, direction })
  }

  const getSortIndicator = (key) => {
    if (sortConfig.key !== key) return ''
    return sortConfig.direction === 'asc' ? ' ▲' : ' ▼'
  }

  // توابع فرمت
  const formatNumber = (num) => {
    if (!num && num !== 0) return '-'
    return new Intl.NumberFormat('fa-IR').format(Number(num))
  }

  const formatPercentage = (value) => {
    if (!value && value !== 0) return '-'
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
        month: '2-digit',
        day: '2-digit',
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
      <div className="social-data-page">
        <header className="header">
          <h1>📊 داده‌های سوشال</h1>
          <nav className="nav-links">
            <Link to="/">داشبورد</Link>
            <Link to="/social-data" className="active">داده‌های سوشال</Link>
            <Link to="/settings">تنظیمات</Link>
            <Link to="/tutorial">آموزش</Link>
            <Link to="/documentation">📚 مستندات</Link>
          </nav>
        </header>
        <div className="loading">
          <div className="spinner"></div>
          <div>در حال بارگذاری داده‌های سوشال...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="social-data-page">
      <header className="header">
        <h1>📊 داده‌های سوشال</h1>
        <nav className="nav-links">
          <Link to="/">داشبورد</Link>
          <Link to="/social-data" className="active">داده‌های سوشال</Link>
          <Link to="/settings">تنظیمات</Link>
          <Link to="/tutorial">آموزش</Link>
          <Link to="/documentation">📚 مستندات</Link>
        </nav>
      </header>

      {error && (
        <div className="error-banner">
          <strong>خطا:</strong> {error}
          <button onClick={() => { setError(null); loadSocialData(); }}>
            تلاش مجدد
          </button>
        </div>
      )}

      <div className="content">
        {/* اطلاعات منبع */}
        <div className="source-info-card">
          <div className="source-header">
            <h2>🌐 اطلاعات منابع داده</h2>
            <button 
              className="refresh-btn"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              {refreshing ? '🔄 در حال به‌روزرسانی...' : '🔄 به‌روزرسانی'}
            </button>
          </div>
          
          {sourceInfo && (
            <div className="source-details">
              <div className="source-stat">
                <span className="stat-label">منابع فعال:</span>
                <span className="stat-value">
                  {sourceInfo.sources?.join(', ') || '-'}
                </span>
              </div>
              <div className="source-stat">
                <span className="stat-label">تعداد از API اول:</span>
                <span className="stat-value">{formatNumber(sourceInfo.api1_count)}</span>
              </div>
              <div className="source-stat">
                <span className="stat-label">تعداد از API دوم:</span>
                <span className="stat-value">{formatNumber(sourceInfo.api2_count)}</span>
              </div>
              <div className="source-stat">
                <span className="stat-label">تعداد کل (ادغام شده):</span>
                <span className="stat-value highlight">{formatNumber(sourceInfo.merged_count)}</span>
              </div>
              <div className="source-stat">
                <span className="stat-label">آخرین به‌روزرسانی:</span>
                <span className="stat-value">{formatDate(sourceInfo.timestamp)}</span>
              </div>
              
              {/* اطلاعات cache */}
              {sourceInfo.cache_info && Object.keys(sourceInfo.cache_info).length > 0 && (
                <div className="cache-info">
                  <h3>📦 وضعیت Cache</h3>
                  {Object.entries(sourceInfo.cache_info).map(([api, info]) => (
                    <div key={api} className="cache-item">
                      <span className="cache-api">{api}:</span>
                      <span className={`cache-status ${info.from_cache ? 'from-cache' : 'fresh'}`}>
                        {info.from_cache ? '📦 از Cache' : '🔄 داده جدید'}
                      </span>
                      {info.last_update && (
                        <span className="cache-time">{formatDate(info.last_update)}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* جستجو و فیلتر */}
        <div className="search-container">
          <input
            type="text"
            placeholder="🔍 جستجو بر اساس نام یا نماد..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <div className="results-count">
            نتایج: {formatNumber(sortedData.length)} از {formatNumber(socialData.length)}
          </div>
        </div>

        {/* جدول داده‌ها */}
        <div className="social-table-container">
          {sortedData.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>داده‌ای یافت نشد</h3>
              <p>
                {searchTerm 
                  ? 'نتیجه‌ای برای جستجوی شما یافت نشد. لطفاً عبارت دیگری جستجو کنید.'
                  : 'داده‌های سوشال هنوز بارگذاری نشده‌اند. لطفاً از داشبورد دکمه "به‌روزرسانی دستی" را بزنید.'}
              </p>
              {!searchTerm && (
                <Link to="/" className="btn btn-primary">
                  رفتن به داشبورد
                </Link>
              )}
            </div>
          ) : (
            <table className="social-table">
              <thead>
                <tr>
                  <th onClick={() => requestSort('symbol')} className="sortable">
                    نماد{getSortIndicator('symbol')}
                  </th>
                  <th onClick={() => requestSort('name')} className="sortable">
                    نام{getSortIndicator('name')}
                  </th>
                  <th onClick={() => requestSort('standing')} className="sortable">
                    Standing{getSortIndicator('standing')}
                  </th>
                  <th onClick={() => requestSort('sentiment')} className="sortable">
                    احساسات{getSortIndicator('sentiment')}
                  </th>
                  <th onClick={() => requestSort('galaxy_score')} className="sortable">
                    Galaxy Score{getSortIndicator('galaxy_score')}
                  </th>
                  <th onClick={() => requestSort('alt_rank')} className="sortable">
                    Alt Rank{getSortIndicator('alt_rank')}
                  </th>
                  <th onClick={() => requestSort('social_volume')} className="sortable">
                    حجم سوشال{getSortIndicator('social_volume')}
                  </th>
                  <th onClick={() => requestSort('social_dominance')} className="sortable">
                    سلطه سوشال{getSortIndicator('social_dominance')}
                  </th>
                  <th onClick={() => requestSort('market_dominance')} className="sortable">
                    سلطه بازار{getSortIndicator('market_dominance')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {sortedData.map((item, index) => (
                  <tr key={item.symbol || index}>
                    <td className="symbol-cell">{item.symbol || '-'}</td>
                    <td className="name-cell">{item.name || '-'}</td>
                    <td className="standing-cell">
                      {item.standing !== null && item.standing !== undefined 
                        ? formatNumber(item.standing) 
                        : '-'}
                    </td>
                    <td className={`sentiment-cell ${getChangeColor(item.sentiment)}`}>
                      {item.sentiment !== null && item.sentiment !== undefined 
                        ? formatPercentage(item.sentiment) 
                        : '-'}
                    </td>
                    <td className="galaxy-cell">
                      {item.galaxy_score !== null && item.galaxy_score !== undefined 
                        ? formatNumber(item.galaxy_score) 
                        : '-'}
                    </td>
                    <td className="alt-rank-cell">
                      {item.alt_rank !== null && item.alt_rank !== undefined 
                        ? `#${formatNumber(item.alt_rank)}` 
                        : '-'}
                    </td>
                    <td className="volume-cell">
                      {item.social_volume !== null && item.social_volume !== undefined 
                        ? formatNumber(item.social_volume) 
                        : '-'}
                    </td>
                    <td className="dominance-cell">
                      {item.social_dominance !== null && item.social_dominance !== undefined 
                        ? formatPercentage(item.social_dominance) 
                        : '-'}
                    </td>
                    <td className="market-dom-cell">
                      {item.market_dominance !== null && item.market_dominance !== undefined 
                        ? formatPercentage(item.market_dominance) 
                        : '-'}
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

export default SocialData
