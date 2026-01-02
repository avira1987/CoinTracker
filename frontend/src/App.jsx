import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import './App.css'

function App() {
  // صفحه لاگین غیرفعال شده است - دسترسی مستقیم به صفحات
  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={<Navigate to="/" replace />} 
        />
        <Route 
          path="/settings" 
          element={<Settings />} 
        />
        <Route 
          path="/" 
          element={<Dashboard />} 
        />
      </Routes>
    </Router>
  )
}

export default App

