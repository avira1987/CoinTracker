import React, { useState } from 'react'
import { login } from '../services/api'
import './Login.css'

function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await login(username, password)
      if (response.data.success) {
        onLogin()
      } else {
        setError(response.data.message || 'خطا در ورود')
      }
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در ارتباط با سرور')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>ورود به سیستم</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>نام کاربری:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="admin34_"
            />
          </div>
          <div className="form-group">
            <label>رمز عبور:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="123asd;p+_"
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'در حال ورود...' : 'ورود'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login

