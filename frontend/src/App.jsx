import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import { checkAuth } from './services/api'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // بررسی وضعیت احراز هویت
    checkAuth()
      .then(response => {
        setIsAuthenticated(response.data.authenticated)
      })
      .catch(() => {
        setIsAuthenticated(false)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}>در حال بارگذاری...</div>
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? <Navigate to="/" /> : <Login onLogin={() => setIsAuthenticated(true)} />
          } 
        />
        <Route 
          path="/settings" 
          element={
            isAuthenticated ? <Settings /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/" 
          element={
            isAuthenticated ? <Dashboard /> : <Navigate to="/login" />
          } 
        />
      </Routes>
    </Router>
  )
}

export default App

