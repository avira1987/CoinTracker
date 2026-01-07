import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import Tutorial from './pages/Tutorial'
import Documentation from './pages/Documentation'
import SocialData from './pages/SocialData'
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
          path="/tutorial" 
          element={<Tutorial />} 
        />
        <Route 
          path="/documentation" 
          element={<Documentation />} 
        />
        <Route 
          path="/social-data" 
          element={<SocialData />} 
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

