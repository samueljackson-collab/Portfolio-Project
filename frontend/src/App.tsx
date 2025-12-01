/**
 * Main App Component
 *
 * Root component with routing configuration
 */

import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context'
import { Navbar, ProtectedRoute } from './components'
import { Home, Login, Register, Dashboard, HomeAssistant, EnterprisePortfolio, PhotosPage, RoamingConsole } from './pages'

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/home-assistant" element={<HomeAssistant />} />
            <Route path="/enterprise-portfolio" element={<EnterprisePortfolio />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/photos"
              element={
                <ProtectedRoute>
                  <PhotosPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/roaming-console"
              element={
                <ProtectedRoute>
                  <RoamingConsole />
                </ProtectedRoute>
              }
            />

            {/* Catch-all redirect */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
