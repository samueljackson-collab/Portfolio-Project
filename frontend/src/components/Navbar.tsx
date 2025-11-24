/**
 * Navbar Component
 *
 * Main navigation bar with authentication-aware links
 */

import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context'

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and primary nav */}
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-2xl font-bold text-primary-600">
                Portfolio
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link
                to="/"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-primary-600 transition-colors"
              >
                Home
              </Link>
              <Link
                to="/enterprise-portfolio"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-primary-600 transition-colors"
              >
                Portfolio Showcase
              </Link>
              {isAuthenticated && (
                <Link
                  to="/dashboard"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-primary-600 transition-colors"
                >
                  Dashboard
                </Link>
              )}
              {isAuthenticated && (
                <Link
                  to="/orchestration"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-primary-600 transition-colors"
                >
                  Orchestration
                </Link>
              )}
            </div>
          </div>

          {/* Right side - auth buttons */}
          <div className="flex items-center">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700">
                  {user?.email}
                </span>
                <button
                  onClick={handleLogout}
                  className="btn-secondary"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="btn-primary"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
