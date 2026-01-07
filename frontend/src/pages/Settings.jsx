import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getSettings, updateSettings } from '../services/api'
import './Settings.css'

function Settings() {
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const response = await getSettings()
      setSettings(response.data)
      setLoading(false)
      setMessage('')
    } catch (error) {
      console.error('Error loading settings:', error)
      const errorMessage = error.response?.data?.error || error.message || 'خطا در بارگذاری تنظیمات'
      setMessage(`خطا در بارگذاری تنظیمات: ${errorMessage}`)
      setLoading(false)
    }
  }

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleWeightChange = (field, value) => {
    const numValue = parseFloat(value) || 0
    setSettings(prev => ({
      ...prev,
      [field]: numValue
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMessage('')

    // بررسی اینکه مجموع وزن‌ها برابر 1 باشد
    const totalWeight = 
      parseFloat(settings.price_weight || 0) +
      parseFloat(settings.volume_weight || 0) +
      parseFloat(settings.stability_weight || 0) +
      parseFloat(settings.market_cap_weight || 0) +
      parseFloat(settings.social_weight || 0)

    if (Math.abs(totalWeight - 1.0) > 0.01) {
      setMessage('مجموع وزن‌ها باید برابر 1 باشد')
      setSaving(false)
      return
    }

    try {
      await updateSettings(settings)
      setMessage('تنظیمات با موفقیت ذخیره شد')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      console.error('Error saving settings:', error)
      setMessage('خطا در ذخیره تنظیمات')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="loading">در حال بارگذاری...</div>
  }

  if (!settings) {
    return <div className="error">خطا در بارگذاری تنظیمات</div>
  }

  const totalWeight = 
    (parseFloat(settings.price_weight) || 0) +
    (parseFloat(settings.volume_weight) || 0) +
    (parseFloat(settings.stability_weight) || 0) +
    (parseFloat(settings.market_cap_weight) || 0) +
    (parseFloat(settings.social_weight) || 0)

  return (
    <div className="settings">
      <header className="header">
        <h1>CoinTracker - تنظیمات</h1>
        <nav className="nav-links">
          <Link to="/">داشبورد</Link>
          <Link to="/settings">تنظیمات</Link>
          <Link to="/tutorial">آموزش</Link>
          <Link to="/documentation">📚 مستندات</Link>
        </nav>
      </header>

      <div className="content">
        <form onSubmit={handleSubmit} className="settings-form">
          {message && (
            <div className={`message ${message.includes('موفقیت') ? 'success' : 'error'}`}>
              {message}
            </div>
          )}

          {/* بخش تنظیمات API */}
          <section className="settings-section">
            <h2>تنظیمات API</h2>
            <div className="form-group">
              <label>کلید API CoinGecko:</label>
              <input
                type="text"
                value={settings.api_key || ''}
                onChange={(e) => handleChange('api_key', e.target.value)}
                placeholder="CG-xxxxxxxxxxxxx"
              />
            </div>
          </section>

          {/* بخش وزن‌های رتبه‌بندی */}
          <section className="settings-section">
            <h2>وزن‌های رتبه‌بندی</h2>
            <div className="weight-info">
              <p>مجموع وزن‌ها باید برابر 1 باشد</p>
              <p className={`total-weight ${Math.abs(totalWeight - 1.0) < 0.01 ? 'valid' : 'invalid'}`}>
                مجموع فعلی: {totalWeight.toFixed(2)}
              </p>
            </div>
            <div className="form-group">
              <label>تغییرات قیمت:</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.price_weight || 0}
                onChange={(e) => handleWeightChange('price_weight', e.target.value)}
              />
              <span className="weight-percent">{((settings.price_weight || 0) * 100).toFixed(0)}%</span>
            </div>
            <div className="form-group">
              <label>تغییرات حجم:</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.volume_weight || 0}
                onChange={(e) => handleWeightChange('volume_weight', e.target.value)}
              />
              <span className="weight-percent">{((settings.volume_weight || 0) * 100).toFixed(0)}%</span>
            </div>
            <div className="form-group">
              <label>پایداری:</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.stability_weight || 0}
                onChange={(e) => handleWeightChange('stability_weight', e.target.value)}
              />
              <span className="weight-percent">{((settings.stability_weight || 0) * 100).toFixed(0)}%</span>
            </div>
            <div className="form-group">
              <label>حجم بازار:</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.market_cap_weight || 0}
                onChange={(e) => handleWeightChange('market_cap_weight', e.target.value)}
              />
              <span className="weight-percent">{((settings.market_cap_weight || 0) * 100).toFixed(0)}%</span>
            </div>
            <div className="form-group">
              <label>سوشال:</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.social_weight || 0}
                onChange={(e) => handleWeightChange('social_weight', e.target.value)}
              />
              <span className="weight-percent">{((settings.social_weight || 0) * 100).toFixed(0)}%</span>
            </div>
          </section>

          {/* بخش تنظیمات نمایش */}
          <section className="settings-section">
            <h2>تنظیمات نمایش</h2>
            <div className="form-group">
              <label>تعداد کوین‌های برتر:</label>
              <input
                type="number"
                min="1"
                max="500"
                value={settings.top_coins_count || 100}
                onChange={(e) => handleChange('top_coins_count', parseInt(e.target.value))}
              />
            </div>
            <div className="form-group">
              <label>روزهای تاریخچه داده (برای محاسبه پایداری):</label>
              <input
                type="number"
                min="1"
                max="30"
                value={settings.data_history_days || 7}
                onChange={(e) => handleChange('data_history_days', parseInt(e.target.value))}
              />
            </div>
            <div className="form-group">
              <label>فاصله به‌روزرسانی (ثانیه):</label>
              <input
                type="number"
                min="10"
                max="3600"
                value={settings.update_interval || 60}
                onChange={(e) => handleChange('update_interval', parseInt(e.target.value))}
              />
            </div>
          </section>

          <div className="form-actions">
            <button type="submit" disabled={saving} className="btn-save">
              {saving ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
            </button>
            <Link to="/" className="btn-cancel">
              انصراف
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Settings

